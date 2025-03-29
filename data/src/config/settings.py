"""Configuration settings for the ad generation data pipeline."""

import os
import warnings

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class AzureOpenAISettings(BaseModel):
    """Azure OpenAI API settings."""

    deployment_name: str = Field(
        default="iprove-gpt-4o-mini", description="The deployment name for the Azure OpenAI model"
    )
    azure_endpoint: str = Field(
        default="https://i-prove.openai.azure.com/", description="The Azure OpenAI endpoint URL"
    )
    api_version: str = Field(default="2024-05-01-preview", description="The Azure OpenAI API version")
    api_key: str = Field(default="", description="The Azure OpenAI API key")
    temperature: float = Field(default=1.0, description="The temperature for the LLM generation")


class PipelineSettings(BaseModel):
    """Settings for the data generation pipeline."""

    num_examples: int = Field(default=5, description="Number of examples to generate per field")
    batch_size: int = Field(default=12, description="Number of fields to process in a batch")
    output_file: str = Field(default="ads.json", description="Path to the output JSON file")
    fixed_output_file: str = Field(default="fixed_ads.json", description="Path to the fixed output JSON file")
    final_output_file: str = Field(
        default="fixed_ads_list.json", description="Path to the final flattened output JSON file"
    )
    retry_attempts: int = Field(default=3, description="Number of retry attempts for failed requests")
    retry_delay: int = Field(default=60, description="Delay between retry attempts in seconds")


class Settings(BaseSettings):
    """Main settings class for the application."""

    azure_openai: AzureOpenAISettings = Field(default_factory=AzureOpenAISettings)
    pipeline: PipelineSettings = Field(default_factory=PipelineSettings)

    class Config:
        """Configuration for the settings class."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


# Create settings instance
settings = Settings()

# Load API key from environment variable if not set
if not settings.azure_openai.api_key:
    settings.azure_openai.api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")

    # Validate API key is set
    if not settings.azure_openai.api_key:
        warnings.warn(
            "AZURE_OPENAI_API_KEY is not set. Please set it as an environment variable "
            "or in the .env file to use the Azure OpenAI API.",
            stacklevel=2,
        )
