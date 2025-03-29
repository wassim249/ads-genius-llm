"""Prompt templates for the ad generation pipeline."""

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from src.schemas import EXAMPLE_DATA, DataEntryList
from src.utils.logging import get_logger

logger = get_logger("data_pipeline.core.prompts")


def create_ad_generation_prompt(output_parser: PydanticOutputParser) -> PromptTemplate:
    """Create the prompt template for ad generation.

    Args:
        output_parser: The PydanticOutputParser instance for parsing the output.

    Returns:
        PromptTemplate: The configured prompt template.
    """
    examples = [example.model_dump_json() for example in EXAMPLE_DATA]
    logger.debug("creating_ad_generation_prompt", examples_count=len(examples))

    return PromptTemplate(
        input_variables=["input_field", "num_examples"],
        template="""As an expert copywriter, generate high-converting ad copy using proven frameworks.
Instructions:

Create a casual user prompt (include natural typos/informal language)
Generate ad copy using these proven elements:

Must Include:

* Hook (Problem-Solution Format)
* Social Proof (numbers, testimonials)
* Benefits with Specific Results
* Urgency/Scarcity
* Risk Reversal (guarantee/trial)
* Clear Call-to-Action
* Trust Signals

Formatting:

* Scannable chunks
* Markdown for emphasis
* Relevant hashtags
* Short paragraphs

Input Field: <<<{input_field}>>>
Format Instructions: <<<{format_instructions}>>>
Examples: <<<{examples}>>>
Generate {num_examples} examples following successful viral ad patterns.
Answer in raw format only.""",
        partial_variables={"format_instructions": output_parser.get_format_instructions(), "examples": examples},
    )


def create_json_fix_prompt(output_parser: PydanticOutputParser) -> PromptTemplate:
    """Create the prompt template for fixing JSON output.

    Args:
        output_parser: The PydanticOutputParser instance for parsing the output.

    Returns:
        PromptTemplate: The configured prompt template.
    """
    logger.debug("creating_json_fix_prompt")

    return PromptTemplate(
        template="""
You are JSON expert, your task is to fix the following JSON file make sure it follows the provided schema.

Schema:
{schema}

JSON:
{json}

!! Return just the JSON object, nothing else, with no json formatting or any special character, just the json object !!

Correct JSON:""",
        input_variables=["json"],
        partial_variables={"schema": output_parser.get_format_instructions()},
    )


def get_output_parser() -> PydanticOutputParser:
    """Get the PydanticOutputParser for the DataEntryList model.

    Returns:
        PydanticOutputParser: The configured output parser.
    """
    logger.debug("creating_output_parser", schema_class="DataEntryList")
    return PydanticOutputParser(pydantic_object=DataEntryList)
