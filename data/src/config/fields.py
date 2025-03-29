"""Field definitions for the ad generation pipeline."""

import json
from pathlib import Path
from typing import Optional

# Get the path to the fields.json file
FIELDS_FILE = Path(__file__).parent / "fields.json"


def load_fields() -> list[str]:
    """Load the list of fields from the fields.json file.

    Returns:
        list[str]: The list of fields.
    """
    with open(FIELDS_FILE) as f:
        data = json.load(f)
    return data["fields"]


def load_field_groups() -> dict[str, list[str]]:
    """Load the field groups from the fields.json file.

    Returns:
        dict[str, list[str]]: The field groups.
    """
    with open(FIELDS_FILE) as f:
        data = json.load(f)
    return data["field_groups"]


def get_field_group(group_name: str) -> Optional[list[str]]:
    """Get a specific field group by name.

    Args:
        group_name: The name of the field group.

    Returns:
        Optional[list[str]]: The list of fields in the group, or None if the group doesn't exist.
    """
    field_groups = load_field_groups()
    return field_groups.get(group_name.lower())


# Load the fields and field groups
FIELDS = load_fields()
FIELD_GROUPS = load_field_groups()
