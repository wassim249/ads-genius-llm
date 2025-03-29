"""Schemas for the API."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Tone(str, Enum):
    """Tone enum for completion API."""

    PROFESSIONAL = "professional"
    PERSUASIVE = "persuasive"
    CASUAL = "casual"
    FRIENDLY = "friendly"


class CompletionRequest(BaseModel):
    """Request schema for completion API."""

    text: str = Field(
        default=...,
        description="Text to complete",
        example="an ad for my new online banking service that focuses on personalized customer service.",
    )  # type: ignore
    temperature: Optional[float] = Field(
        default=0.7,
        description="Temperature for sampling",
        example=0.7,
        ge=0.0,
        le=1.0,
    )
    max_new_tokens: Optional[int] = Field(
        default=200,
        description="Maximum number of tokens to generate",
        example=200,
        gt=0,
        le=500,
    )
    top_p: Optional[float] = Field(
        default=0.9,
        description="Nucleus sampling parameter",
        example=0.9,
        ge=0.0,
        le=1.0,
    )
    top_k: Optional[int] = Field(
        default=50,
        description="Top-k sampling parameter",
        example=50,
        gt=0,
        le=100,
    )
    repetition_penalty: Optional[float] = Field(
        default=1.1,
        description="Repetition penalty parameter",
        example=1.1,
        ge=1.0,
        le=2.0,
    )
    tone: Optional[Tone] = Field(
        default=Tone.PROFESSIONAL,
        description="Tone to use for generation",
        example=Tone.PROFESSIONAL,
    )

    class Config:
        """Config for the completion request."""

        json_schema_extra = {
            "example": {
                "text": "The weather today is",
                "max_length": 128,
                "temperature": 0.7,
                "max_new_tokens": 200,
                "top_p": 0.9,
                "top_k": 50,
                "repetition_penalty": 1.1,
                "tones": ["professional", "persuasive"],
            }
        }


class CompletionMetadata(BaseModel):
    """Metadata for the completion."""

    input_tokens: int = Field(default=..., description="Number of input tokens", example=10)  # type: ignore
    output_tokens: int = Field(default=..., description="Number of output tokens", example=10)  # type: ignore


class CompletionResponse(BaseModel):
    """Response schema for completion API."""

    completions: list[str] = Field(  # type: ignore
        default=...,
        description="List of generated completions",
        example=[
            "The weather today is sunny",
            "The weather today is nice",
            "The weather today is warm",
        ],
    )
    metadata: CompletionMetadata = Field(  # type: ignore
        default=...,
        description="Metadata about the completion",
        example=CompletionMetadata(input_tokens=10, output_tokens=10),
    )
