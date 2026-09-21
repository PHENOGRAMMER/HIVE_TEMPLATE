from __future__ import annotations

from datetime import date, datetime
import html
from typing import Any

import pandas as pd

from app.schemas.template import (
    ImportedField,
    ImportedItem,
    ImportedSection,
    ImportedTemplate,
)


COMMENT_TYPE_COLUMN = "Comment Type (info, limit, defect)"
CATEGORY_COLUMN = "Category (-1: Low, 0: Med, 1: High)"
OPTIONS_COLUMN = "Multiple Choice Options (comma-separated)"
UNIT_OPTIONS_COLUMN = (
    "Unit Type Options (numeric answers only, comma-separated)"
)
RECOMMENDATION_COLUMN = "Recommendation (from list)"
ORDER_COLUMN = "Order (w/i item)"
ANSWER_TYPE_COLUMN = (
    "Answer Type (boolean, checkbox, date, number, range, text)"
)
DEFAULT_VALUE_COLUMN = "Default Value"
DEFAULT_VALUE_2_COLUMN = 'Default Value 2 (for "range" types)'
DEFAULT_UNIT_COLUMN = 'Default Unit Type (for "number" and "range" types)'
DEFAULT_LOCATION_COLUMN = "Default Location"
ESTIMATE_MIN_COLUMN = "Default Estimate Min"
ESTIMATE_MAX_COLUMN = "Default Estimate Max"
LOCKED_COLUMN = "Locked"
SIMPLE_FORMAT_COLUMN = "Simple Format"
DISABLE_PHOTOS_COLUMN = "Disable Photos"
USES_COLUMN = "Uses"


CORE_COLUMNS = {
    "Section Name",
    "Item Name",
    "Comment Name",
    "Comment Text",
    COMMENT_TYPE_COLUMN,
    CATEGORY_COLUMN,
    OPTIONS_COLUMN,
    UNIT_OPTIONS_COLUMN,
    RECOMMENDATION_COLUMN,
    ORDER_COLUMN,
    ANSWER_TYPE_COLUMN,
    DEFAULT_VALUE_COLUMN,
    DEFAULT_VALUE_2_COLUMN,
    DEFAULT_UNIT_COLUMN,
    DEFAULT_LOCATION_COLUMN,
    ESTIMATE_MIN_COLUMN,
    ESTIMATE_MAX_COLUMN,
    LOCKED_COLUMN,
    SIMPLE_FORMAT_COLUMN,
    DISABLE_PHOTOS_COLUMN,
    USES_COLUMN,
}


def is_empty(value: Any) -> bool:
    """Return True for None, NaN, or blank strings."""
    if value is None:
        return True

    if pd.isna(value):
        return True

    if isinstance(value, str) and not value.strip():
        return True

    return False


def normalize_metadata_value(value: Any) -> Any:
    """
    Convert spreadsheet values into JSON-serializable values.
    """

    if is_empty(value):
        return None

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if hasattr(value, "item"):
        value = value.item()

    return value


def extract_source_metadata(row: pd.Series) -> dict[str, Any]:
    """
    Preserve source columns that aren't represented by
    dedicated core fields.
    """

    metadata: dict[str, Any] = {}

    for column in row.index:
        if column in CORE_COLUMNS:
            continue

        metadata[column] = normalize_metadata_value(
            row[column]
        )

    return metadata


def clean_optional(value: Any) -> str | None:
    """Convert an optional spreadsheet value into clean display text."""
    if is_empty(value):
        return None

    return html.unescape(str(value).strip())


def to_int(value: Any) -> int | None:
    """Convert a spreadsheet value to int safely."""
    if is_empty(value):
        return None

    return int(float(value))


def to_float(value: Any) -> float | None:
    """Convert a spreadsheet value to float safely."""
    if is_empty(value):
        return None

    return float(value)


def to_bool(value: Any) -> bool | None:
    """Convert common spreadsheet boolean representations."""
    if is_empty(value):
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return bool(value)

    normalized = str(value).strip().lower()

    if normalized in {"true", "yes", "1"}:
        return True

    if normalized in {"false", "no", "0"}:
        return False

    return None


def parse_csv(value: Any) -> list[str]:
    """
    Parse a comma-separated Spectora field.

    Empty values become an empty list.
    """
    if is_empty(value):
        return []

    return [
        part.strip()
        for part in str(value).split(",")
        if part.strip()
    ]


def map_row(row: pd.Series, source_row: int) -> ImportedField:
    """Map one Spectora spreadsheet row to ImportedField."""

    return ImportedField(
        name=str(row["Comment Name"]).strip(),
        comment_text=(
            None
            if is_empty(row["Comment Text"])
            else str(row["Comment Text"]).strip()
        ),
        comment_type=str(row[COMMENT_TYPE_COLUMN]).strip().lower(),
        category=to_int(row[CATEGORY_COLUMN]),
        answer_type=str(row[ANSWER_TYPE_COLUMN]).strip().lower(),
        options=parse_csv(row[OPTIONS_COLUMN]),
        unit_options=parse_csv(row[UNIT_OPTIONS_COLUMN]),
        recommendation=clean_optional(row[RECOMMENDATION_COLUMN]),
        order=to_int(row[ORDER_COLUMN]),
        default_value=(
            None
            if is_empty(row[DEFAULT_VALUE_COLUMN])
            else row[DEFAULT_VALUE_COLUMN]
        ),
        default_value_2=(
            None
            if is_empty(row[DEFAULT_VALUE_2_COLUMN])
            else row[DEFAULT_VALUE_2_COLUMN]
        ),
        default_unit_type=clean_optional(
            row[DEFAULT_UNIT_COLUMN]
        ),
        default_location=clean_optional(
            row[DEFAULT_LOCATION_COLUMN]
        ),
        estimate_min=to_float(row[ESTIMATE_MIN_COLUMN]),
        estimate_max=to_float(row[ESTIMATE_MAX_COLUMN]),
        locked=to_bool(row[LOCKED_COLUMN]),
        simple_format=to_bool(row[SIMPLE_FORMAT_COLUMN]),
        disable_photos=to_bool(row[DISABLE_PHOTOS_COLUMN]),
        uses=to_int(row[USES_COLUMN]),
        source_row=source_row,
        source_metadata=extract_source_metadata(row),
    )


def map_dataframe(
    df: pd.DataFrame,
    template_name: str,
    source_file: str,
) -> ImportedTemplate:
    """
    Convert an entire Spectora DataFrame into a structured template.

    Source row order is preserved. Section and item positions are based
    on their first appearance in the spreadsheet.
    """

    sections: list[ImportedSection] = []

    section_lookup: dict[str, ImportedSection] = {}
    item_lookup: dict[tuple[str, str], ImportedItem] = {}

    for dataframe_index, row in df.iterrows():
        source_row = dataframe_index + 2

        section_name = html.unescape(
            str(row["Section Name"]).strip()
        )

        item_name = html.unescape(
            str(row["Item Name"]).strip()
        )

        # Create the section only when first encountered.
        if section_name not in section_lookup:
            section = ImportedSection(
                name=section_name,
                position=len(sections),
                items=[],
            )

            sections.append(section)
            section_lookup[section_name] = section

        section = section_lookup[section_name]

        item_key = (section_name, item_name)

        # Create the item only when first encountered.
        if item_key not in item_lookup:
            item = ImportedItem(
                name=item_name,
                position=len(section.items),
                fields=[],
            )

            section.items.append(item)
            item_lookup[item_key] = item

        item = item_lookup[item_key]

        # Each spreadsheet row becomes exactly one field.
        field = map_row(row, source_row=source_row)
        item.fields.append(field)

    return ImportedTemplate(
        name=template_name,
        source="Spectora",
        source_file=source_file,
        sections=sections,
    )