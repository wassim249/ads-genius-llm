"""Configuration package for the ad generation pipeline."""

from data.src.data_pipeline.config.fields import FIELD_GROUPS, FIELDS, get_field_group
from data.src.data_pipeline.config.settings import settings

__all__ = ["settings", "FIELDS", "FIELD_GROUPS", "get_field_group"]
