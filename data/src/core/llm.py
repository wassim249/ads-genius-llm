"""LLM client setup for the ad generation pipeline."""

from langchain_openai import AzureChatOpenAI
from tenacity import retry, stop_after_attempt, wait_fixed

from src.config import settings
from src.utils.logging import get_logger

logger = get_logger("data_pipeline.core.llm")


def get_azure_openai_client() -> AzureChatOpenAI:
    """Get the Azure OpenAI client with the configured settings.

    Returns:
        AzureChatOpenAI: The configured Azure OpenAI client.
    """
    logger.debug(
        "initializing_azure_openai_client",
        deployment_name=settings.azure_openai.deployment_name,
        endpoint=settings.azure_openai.azure_endpoint,
        api_version=settings.azure_openai.api_version,
        temperature=settings.azure_openai.temperature,
    )

    client = AzureChatOpenAI(
        deployment_name=settings.azure_openai.deployment_name,
        azure_endpoint=settings.azure_openai.azure_endpoint,
        api_version=settings.azure_openai.api_version,
        api_key=settings.azure_openai.api_key,
        temperature=settings.azure_openai.temperature,
    )

    logger.debug("azure_openai_client_initialized")
    return client


def log_retry_attempt(retry_state):
    """Log retry attempts."""
    logger.warning(
        "retry_attempt",
        attempt_number=retry_state.attempt_number,
        next_action="retrying" if retry_state.attempt_number < settings.pipeline.retry_attempts else "giving up",
        wait_time=retry_state.next_action.sleep if hasattr(retry_state.next_action, "sleep") else None,
        exception=str(retry_state.outcome.exception()) if retry_state.outcome.failed else None,
    )


@retry(
    stop=stop_after_attempt(settings.pipeline.retry_attempts),
    wait=wait_fixed(settings.pipeline.retry_delay),
    before_sleep=log_retry_attempt,
)
def generate_with_retry(llm, prompt, **kwargs):
    """Generate text with the LLM with retry logic.

    Args:
        llm: The LLM client.
        prompt: The prompt to send to the LLM.
        **kwargs: Additional arguments to pass to the LLM.

    Returns:
        The LLM response.
    """
    logger.debug("generating_text", prompt_length=len(prompt))
    try:
        response = llm.invoke(prompt, **kwargs)
        logger.debug("text_generated", response_length=len(response.content))
        return response
    except Exception as e:
        logger.error("generation_failed", error=str(e), error_type=type(e).__name__)
        raise
