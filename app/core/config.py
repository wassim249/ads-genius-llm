"""Configuration for the application."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the application."""

    PROJECT_NAME: str = "Ads Genius AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ALLOWED_ORIGINS: list[str] = ["*"]

    # Model settings
    BASE_MODEL: str = "google/gemma-3-1b-it"
    LORA_WEIGHTS: str = "wassim249/ads-genius-gemma-3-1b-it-finetuned"
    DEFAULT_MAX_NEW_TOKENS: int = 32
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_TOP_P: float = 0.95
    DEFAULT_TOP_K: int = 50
    DEFAULT_DO_SAMPLE: bool = True
    DEFAULT_REPETITION_PENALTY: float = 1.1
    DEVICE: str = "cuda"  # or "cpu"
    OFFLOAD_DIR: str = "offload_folder"  # Directory for model offloading

    # Performance settings
    WORKERS_PER_CORE: float = 1.0
    MAX_WORKERS: int = 16
    TIMEOUT: int = 300
    MAX_PARALLEL_REQUESTS: int = 5  # Maximum number of parallel inference requests


@lru_cache
def get_settings() -> Settings:
    """Get the settings for the application."""
    return Settings()
