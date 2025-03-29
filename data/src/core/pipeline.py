"""Main pipeline functionality for ad generation."""

import time
from typing import Optional

from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from src.config import FIELDS, settings
from src.core.llm import generate_with_retry, get_azure_openai_client
from src.core.prompts import (
    create_ad_generation_prompt,
    create_json_fix_prompt,
    get_output_parser,
)
from src.utils.file_utils import (
    flatten_entries,
    get_fields_batch,
    load_json_file,
    save_json_file,
)
from src.utils.logging import get_logger

logger = get_logger("data_pipeline.core.pipeline")


def process_batch(
    fields_batch: list[str],
    llm,
    prompt_template: PromptTemplate,
    output_parser: PydanticOutputParser,
    num_examples: int,
) -> list[dict]:
    """Process a batch of fields to generate ad copy.

    Args:
        fields_batch: The batch of fields to process.
        llm: The LLM client.
        prompt_template: The prompt template.
        output_parser: The output parser.
        num_examples: The number of examples to generate per field.

    Returns:
        A list of generated ad entries.
    """
    logger.info("processing_batch_started", fields=fields_batch, num_examples=num_examples)

    # Prepare batch inputs
    batch_inputs = [{"input_field": field, "num_examples": num_examples} for field in fields_batch]

    # Generate responses
    results = []
    for input_data in batch_inputs:
        field = input_data["input_field"]
        logger.debug("processing_field", field=field)

        try:
            prompt = prompt_template.format(**input_data)
            logger.debug("prompt_created", field=field, prompt_length=len(prompt))

            response = generate_with_retry(llm, prompt)
            logger.debug("llm_response_received", field=field, response_length=len(response.content))

            parsed_result = output_parser.parse(response.content)
            results.append(parsed_result.model_dump())
            logger.info("field_processed_successfully", field=field, entries_count=len(parsed_result.entries))

        except OutputParserException as e:
            logger.error(
                "output_parsing_failed",
                field=field,
                error=str(e),
                error_type="OutputParserException",
                response=response.content if "response" in locals() else None,
            )
            # Store the raw response for later fixing
            results.append(
                {
                    "field": field,
                    "raw_response": response.content if "response" in locals() else None,
                }
            )
        except Exception as e:
            logger.error("field_processing_failed", field=field, error=str(e), error_type=type(e).__name__)
            results.append({"field": field, "error": str(e)})

    logger.info("processing_batch_completed", successful_count=len([r for r in results if "field" not in r]))
    return results


def fix_failed_responses(
    failed_responses: list[dict], llm, fix_prompt_template: PromptTemplate, output_parser: PydanticOutputParser
) -> list[dict]:
    """Fix failed responses using a JSON fixing prompt.

    Args:
        failed_responses: The list of failed responses.
        llm: The LLM client.
        fix_prompt_template: The prompt template for fixing JSON.
        output_parser: The output parser.

    Returns:
        A list of fixed responses.
    """
    fixed_results = []
    logger.info("fixing_failed_responses_started", count=len(failed_responses))

    for response in failed_responses:
        if "raw_response" not in response:
            logger.warning("skipping_response_without_raw_data", field=response.get("field", "unknown"))
            continue

        field = response.get("field", "unknown")
        logger.debug("fixing_response", field=field)

        try:
            prompt = fix_prompt_template.format(json=response["raw_response"])
            fixed_response = generate_with_retry(llm, prompt)
            parsed_result = output_parser.parse(fixed_response.content)
            fixed_results.append(parsed_result.model_dump())
            logger.info("response_fixed_successfully", field=field)
        except Exception as e:
            logger.error("response_fixing_failed", field=field, error=str(e), error_type=type(e).__name__)

    logger.info("fixing_failed_responses_completed", fixed_count=len(fixed_results))
    return fixed_results


def main(
    fields: Optional[list[str]] = None,
    output_file: Optional[str] = None,
    fixed_output_file: Optional[str] = None,
    final_output_file: Optional[str] = None,
    batch_size: Optional[int] = None,
    num_examples: Optional[int] = None,
    retry_delay: Optional[int] = None,
):
    """Main function to run the ad generation pipeline.

    Args:
        fields: The list of fields to process. Defaults to FIELDS.
        output_file: The path to the output file. Defaults to settings.pipeline.output_file.
        fixed_output_file: The path to the fixed output file. Defaults to settings.pipeline.fixed_output_file.
        final_output_file: The path to the final output file. Defaults to settings.pipeline.final_output_file.
        batch_size: The batch size. Defaults to settings.pipeline.batch_size.
        num_examples: The number of examples to generate per field. Defaults to settings.pipeline.num_examples.
        retry_delay: The delay between batches in seconds. Defaults to settings.pipeline.retry_delay.
    """
    # Check if API key is set
    if not settings.azure_openai.api_key:
        logger.error(
            "api_key_not_found",
            message="Please set the AZURE_OPENAI_API_KEY environment variable or add it to .env file.",
        )
        return

    # Use default values if not provided
    fields = fields or FIELDS
    output_file = output_file or settings.pipeline.output_file
    fixed_output_file = fixed_output_file or settings.pipeline.fixed_output_file
    final_output_file = final_output_file or settings.pipeline.final_output_file
    batch_size = batch_size or settings.pipeline.batch_size
    num_examples = num_examples or settings.pipeline.num_examples
    retry_delay = retry_delay or settings.pipeline.retry_delay

    logger.info(
        "pipeline_started",
        fields_count=len(fields),
        batch_size=batch_size,
        num_examples=num_examples,
        output_file=output_file,
        fixed_output_file=fixed_output_file,
        final_output_file=final_output_file,
    )

    # Initialize LLM client
    llm = get_azure_openai_client()
    logger.debug("llm_client_initialized")

    # Initialize output parser
    output_parser = get_output_parser()
    logger.debug("output_parser_initialized")

    # Create prompt templates
    ad_prompt = create_ad_generation_prompt(output_parser)
    fix_prompt = create_json_fix_prompt(output_parser)
    logger.debug("prompt_templates_created")

    # Load existing results if any
    results = load_json_file(output_file, [])
    logger.info("existing_results_loaded", count=len(results))

    failed_responses = []

    # Process fields in batches
    total_batches = (len(fields) + batch_size - 1) // batch_size
    for batch_idx, start_idx in enumerate(range(0, len(fields), batch_size)):
        fields_batch = get_fields_batch(fields, start_idx, batch_size)
        logger.info(
            "processing_batch",
            batch_number=batch_idx + 1,
            total_batches=total_batches,
            start_idx=start_idx,
            end_idx=start_idx + len(fields_batch),
        )

        batch_results = process_batch(fields_batch, llm, ad_prompt, output_parser, num_examples)

        # Separate successful and failed responses
        batch_success = 0
        batch_failed = 0
        for result in batch_results:
            if "raw_response" in result:
                failed_responses.append(result)
                batch_failed += 1
            else:
                results.append(result)
                batch_success += 1

        logger.info("batch_completed", batch_number=batch_idx + 1, successful=batch_success, failed=batch_failed)

        # Save intermediate results
        save_json_file(output_file, results)
        logger.debug("intermediate_results_saved", file=output_file)

        if batch_idx < total_batches - 1:  # Don't sleep after the last batch
            logger.info("sleeping_before_next_batch", delay_seconds=retry_delay)
            time.sleep(retry_delay)

    # Fix failed responses
    fixed_results = []
    if failed_responses:
        logger.info("fixing_failed_responses", count=len(failed_responses))
        fixed_results = fix_failed_responses(failed_responses, llm, fix_prompt, output_parser)

        # Save fixed results
        save_json_file(fixed_output_file, fixed_results)
        logger.info("fixed_results_saved", count=len(fixed_results), file=fixed_output_file)

        # Combine all results
        all_results = results + fixed_results
    else:
        all_results = results
        logger.info("no_failed_responses_to_fix")

    # Flatten and save final results
    flattened_results = flatten_entries(all_results)
    save_json_file(final_output_file, flattened_results)
    logger.info("final_results_saved", count=len(flattened_results), file=final_output_file)

    # Log pipeline completion
    logger.info(
        "pipeline_completed",
        total_fields=len(fields),
        successful=len(results),
        fixed=len(fixed_results),
        final_count=len(flattened_results),
        success_rate=f"{(len(results) + len(fixed_results)) / len(fields) * 100:.2f}%",
    )
