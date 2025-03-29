"""LLM service class for loading and generating completions."""

import os
import warnings

import numexpr as ne  # type: ignore
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, logging  # type: ignore

from app.api.schemas import CompletionMetadata, CompletionResponse, Tone
from app.core.app_logging import get_logger
from app.core.config import get_settings
from app.services.redis_service import RedisService

# Configure transformers logging
logging.set_verbosity_error()
warnings.filterwarnings("ignore")

# Configure NumExpr threads
ne.set_num_threads(ne.detect_number_of_cores())

logger = get_logger(__name__)
settings = get_settings()


class LLMService:
    """LLMService class for loading and generating completions."""

    _instance = None
    redis_service = RedisService()
    def __new__(cls):
        """Singleton pattern for LLMService."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.device = torch.device(settings.DEVICE if torch.cuda.is_available() else "cpu")
            cls._instance.tokenizer = None
            cls._instance.model = None
            print("Loading model")
            cls._instance.load_model()
        return cls._instance

    def __init__(self):
        """Initialize is handled in __new__ for singleton pattern."""
        pass

    # @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def load_model(self):
        """Load LLM model and tokenizer with retry logic.

        Args:
            self: The LLMService instance

        Returns:
            None

        Raises:
            Exception: If the model fails to load
        """
        try:
            logger.info("Loading LLM model and tokenizer", model_name=settings.BASE_MODEL)

            # Suppress unnecessary warnings during model loading
            os.environ["TRANSFORMERS_VERBOSITY"] = "error"
            os.environ["TOKENIZERS_PARALLELISM"] = "true"

            # Set GPU memory settings if using CUDA
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                logger.info("Using CUDA device", device=str(self.device))

            logger.info("Loading tokenizer", model_name=settings.BASE_MODEL)
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(
                    settings.BASE_MODEL, use_fast=True, progress_bar=True, trust_remote_code=True, timeout=60
                )
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                logger.info("Tokenizer loaded successfully")
            except Exception as e:
                logger.error("Failed to load tokenizer", error=str(e))
                raise

            logger.info("Loading model", model_name=settings.BASE_MODEL)
            try:
                self._base_model = AutoModelForCausalLM.from_pretrained(
                    settings.BASE_MODEL,
                    trust_remote_code=True,
                    low_cpu_mem_usage=True,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto",
                    offload_folder=settings.OFFLOAD_DIR,
                )

                # # Create offload directory if it doesn't exist
                # os.makedirs(settings.OFFLOAD_DIR, exist_ok=True)
                # from peft import PeftModel
                # self.model = PeftModel.from_pretrained(
                #     self._base_model,
                #     settings.LORA_WEIGHTS,
                #     torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                #     device_map="auto",
                #     offload_folder=settings.OFFLOAD_DIR,
                # )
                self.model = AutoModelForCausalLM.from_pretrained(
                    "wassim249/ads-genius-gemma-3-1b-it-finetuned-merged",
                    trust_remote_code=True,
                    low_cpu_mem_usage=True,
                    device_map="auto",
                )
                self.model.to(self.device)
                self.model.eval()
                logger.info("Model loaded successfully", device=str(self.device))
            except Exception as e:
                logger.error("Failed to load model", error=str(e))
                raise

            torch.set_grad_enabled(False)
            logger.info("Model initialization complete", device=str(self.device))

        except Exception as e:
            logger.error("Critical failure in model loading", error=str(e))
            raise RuntimeError(f"Failed to initialize model: {str(e)}")

    @torch.no_grad()
    async def get_completion(
        self,
        text: str,
        max_new_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        do_sample: bool | None = None,
        repetition_penalty: float | None = None,
        tone: str | None = None,
    ) -> CompletionResponse:
        """Get LLM completions by appending predictions at the end of the text.

        Args:
            text: Input text to generate completion for
            max_new_tokens: Maximum number of new tokens to generate
            temperature: Sampling temperature (higher = more random)
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            do_sample: Whether to use sampling vs greedy decoding
            repetition_penalty: Penalty for repeating tokens
            tone: Tone for the generated text

        Returns:
            CompletionResponse with generated text and metadata
        """
        try:
            # Use provided values or defaults from settings
            max_new_tokens = max_new_tokens or settings.DEFAULT_MAX_NEW_TOKENS
            temperature = temperature or settings.DEFAULT_TEMPERATURE
            top_p = top_p or settings.DEFAULT_TOP_P
            top_k = top_k or settings.DEFAULT_TOP_K
            do_sample = do_sample if do_sample is not None else settings.DEFAULT_DO_SAMPLE
            repetition_penalty = repetition_penalty or settings.DEFAULT_REPETITION_PENALTY
            tone = tone or Tone.PROFESSIONAL

            # Incorporate tone into the prompt if provided
            if tone:
                prompt = f"Create an ad copy in a {tone} tone for the following:\n\n{text}"
            else:
                prompt = f"Create an ad copy for the following:\n\n{text}"

            # Check if the prompt is already cached in Redis
            cached_completion = await self.redis_service.get_completion(prompt)
            if cached_completion:
                return CompletionResponse(
                    completions=[cached_completion],
                    metadata=CompletionMetadata(input_tokens=len(prompt), output_tokens=len(cached_completion)),
                )

            messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]

            text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

            # Tokenize input
            inputs = self.tokenizer(
                [text],
                return_tensors="pt",
                max_length=max_new_tokens,
                truncation=True,
                padding=True,
            )
            inputs = inputs.to(self.device)
            # Get model predictions
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                num_beams=5,
                top_p=top_p,
                top_k=top_k,
                do_sample=do_sample,
                repetition_penalty=repetition_penalty,
            )

            # Decode the generated tokens
            completions = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
            print(completions)
            if "\nmodel\n" in completions[0]:
                completions[0] = completions[0].split("\nmodel\n")[-1]
            # Cache the completion in Redis
            await self.redis_service.set_completion(prompt, completions[0])

            return CompletionResponse(
                completions=completions,
                metadata=CompletionMetadata(
                    input_tokens=inputs["input_ids"].shape[1],
                    output_tokens=outputs.shape[1],
                ),
            )
        except Exception as e:
            logger.error("Error in model inference", error=str(e))
            raise


def get_model_service() -> LLMService:
    """Get the singleton instance of LLMService."""
    return LLMService()
