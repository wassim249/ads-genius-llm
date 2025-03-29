#!/usr/bin/env python
"""Command-line interface for the ad generation data pipeline."""

import argparse
import logging
import os
import sys
from typing import Optional

from src import main
from src.config import FIELD_GROUPS, FIELDS
from src.config.settings import settings
from src.utils.logging import get_logger, setup_logging

logger = get_logger("cli")


def parse_fields(fields_arg: Optional[str]) -> Optional[list[str]]:
    """Parse the fields argument.

    Args:
        fields_arg: Comma-separated list of fields or a predefined group name.

    Returns:
        list of fields or None to use all fields.
    """
    if not fields_arg:
        return None

    # Check if it's a predefined group
    if fields_arg.lower() in FIELD_GROUPS:
        logger.info("using_predefined_field_group", group=fields_arg.lower())
        return FIELD_GROUPS[fields_arg.lower()]

    # Otherwise, parse as comma-separated list
    parsed_fields = [field.strip() for field in fields_arg.split(",")]

    # Validate fields
    invalid_fields = [field for field in parsed_fields if field not in FIELDS]
    if invalid_fields:
        logger.warning("invalid_fields_specified", invalid_fields=invalid_fields)
        print(f"Warning: The following fields are not in the predefined list: {', '.join(invalid_fields)}")

    return parsed_fields


def run_cli():
    """Run the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Ad Generation Data Pipeline CLI", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Pipeline configuration
    parser.add_argument(
        "--fields",
        help="Comma-separated list of fields to process, or a predefined group (tech, finance, health, education, entertainment, demo). Leave empty to use all fields.",
    )
    parser.add_argument("--output-dir", default="data", help="Directory to store output files")
    parser.add_argument("--output-file", help="Path to the output JSON file")
    parser.add_argument("--fixed-output-file", help="Path to the fixed output JSON file")
    parser.add_argument("--final-output-file", help="Path to the final flattened output JSON file")
    parser.add_argument(
        "--batch-size",
        type=int,
        help=f"Number of fields to process in a batch (default: {settings.pipeline.batch_size})",
    )
    parser.add_argument(
        "--num-examples",
        type=int,
        help=f"Number of examples to generate per field (default: {settings.pipeline.num_examples})",
    )
    parser.add_argument(
        "--retry-delay", type=int, help=f"Delay between batches in seconds (default: {settings.pipeline.retry_delay})"
    )

    # Logging configuration
    parser.add_argument(
        "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO", help="Set the logging level"
    )
    parser.add_argument("--no-console-log", action="store_true", help="Disable console logging")
    parser.add_argument("--no-file-log", action="store_true", help="Disable file logging")

    # Parse arguments
    args = parser.parse_args()

    # Configure logging
    log_level = getattr(logging, args.log_level)
    setup_logging(log_level=log_level, console=not args.no_console_log, file=not args.no_file_log)
    logger.debug("logging_configured", level=args.log_level)

    # Check if API key is set
    if not settings.azure_openai.api_key:
        logger.error(
            "api_key_not_found",
            message="Please set the AZURE_OPENAI_API_KEY environment variable or add it to .env file.",
        )
        print("\nAPI key not found. Please set it using one of these methods:")
        print("1. Export as environment variable:")
        print("   export AZURE_OPENAI_API_KEY=your_api_key")
        print("2. Add to .env file in the project root:")
        print("   AZURE_OPENAI_API_KEY=your_api_key")
        sys.exit(1)

    # Create output directory if specified
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
        logger.debug("output_directory_created", path=args.output_dir)

    # Parse fields
    fields = parse_fields(args.fields)

    # Set output file paths
    output_file = args.output_file
    fixed_output_file = args.fixed_output_file
    final_output_file = args.final_output_file

    # If output_dir is specified but not the specific files, use default names in that directory
    if args.output_dir and not output_file:
        output_file = os.path.join(args.output_dir, settings.pipeline.output_file)
    if args.output_dir and not fixed_output_file:
        fixed_output_file = os.path.join(args.output_dir, settings.pipeline.fixed_output_file)
    if args.output_dir and not final_output_file:
        final_output_file = os.path.join(args.output_dir, settings.pipeline.final_output_file)

    # Log configuration
    logger.info(
        "pipeline_configuration",
        fields_count=len(fields) if fields else len(FIELDS),
        output_file=output_file,
        fixed_output_file=fixed_output_file,
        final_output_file=final_output_file,
        batch_size=args.batch_size or settings.pipeline.batch_size,
        num_examples=args.num_examples or settings.pipeline.num_examples,
        retry_delay=args.retry_delay or settings.pipeline.retry_delay,
    )

    # Run the pipeline
    try:
        main(
            fields=fields,
            output_file=output_file,
            fixed_output_file=fixed_output_file,
            final_output_file=final_output_file,
            batch_size=args.batch_size,
            num_examples=args.num_examples,
            retry_delay=args.retry_delay,
        )
        logger.info("pipeline_execution_completed")
        return 0
    except Exception as e:
        logger.error("pipeline_execution_failed", error=str(e), error_type=type(e).__name__)
        print(f"\nError: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(run_cli())
