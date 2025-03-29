"""File utility functions for the ad generation pipeline."""

import json
import os
from typing import Any, Optional

from src.utils.logging import get_logger

logger = get_logger("data_pipeline.utils.file_utils")


def ensure_directory_exists(file_path: str) -> None:
    """Ensure the directory for a file exists.

    Args:
        file_path: The path to the file.
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        logger.debug("directory_created", path=directory)


def load_json_file(file_path: str, default: Optional[Any] = None) -> Any:
    """Load a JSON file.

    Args:
        file_path: The path to the JSON file.
        default: The default value to return if the file doesn't exist or is invalid.

    Returns:
        The loaded JSON data or the default value.
    """
    if not os.path.exists(file_path):
        logger.debug("file_not_found", file_path=file_path, using_default=True)
        return default if default is not None else []

    try:
        with open(file_path) as f:
            data = json.load(f)
        logger.debug("file_loaded", file_path=file_path, data_size=len(str(data)))
        return data
    except json.JSONDecodeError as e:
        logger.error("json_decode_error", file_path=file_path, error=str(e))
        return default if default is not None else []


def save_json_file(file_path: str, data: Any) -> None:
    """Save data to a JSON file.

    Args:
        file_path: The path to the JSON file.
        data: The data to save.
    """
    ensure_directory_exists(file_path)

    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        logger.debug("file_saved", file_path=file_path, data_size=len(str(data)))
    except Exception as e:
        logger.error("file_save_error", file_path=file_path, error=str(e), error_type=type(e).__name__)


def flatten_entries(entries: list[dict]) -> list[dict]:
    """Flatten a list of entries that may contain nested entries.

    Args:
        entries: The list of entries to flatten.

    Returns:
        The flattened list of entries.
    """
    flattened = []

    for entry in entries:
        if isinstance(entry, dict) and "entries" in entry:
            flattened.extend(entry["entries"])
        else:
            flattened.append(entry)

    logger.debug("entries_flattened", input_count=len(entries), output_count=len(flattened))
    return flattened


def get_fields_batch(fields: list[str], start_idx: int, batch_size: int) -> list[str]:
    """Get a batch of fields from the list.

    Args:
        fields: The list of fields.
        start_idx: The starting index.
        batch_size: The batch size.

    Returns:
        A batch of fields.
    """
    end_idx = min(start_idx + batch_size, len(fields))
    batch = fields[start_idx:end_idx]
    logger.debug("fields_batch_created", start_idx=start_idx, end_idx=end_idx, batch_size=len(batch))
    return batch
