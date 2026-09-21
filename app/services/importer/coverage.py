from __future__ import annotations

import re
from typing import Any

import pandas as pd

from app.schemas.template import (
    ImportedTemplate,
    MigrationCoverage,
)


PHOTO_COLUMN_PATTERN = re.compile(
    r"^Default Photo \d+$"
)

HTML_PATTERN = re.compile(
    r"<[a-zA-Z][^>]*>"
)

LINK_PATTERN = re.compile(
    r"<a\s+[^>]*href\s*=",
    re.IGNORECASE,
)


def _flatten_fields(
    template: ImportedTemplate,
):
    for section in template.sections:
        for item in section.items:
            for field in item.fields:
                yield field


def calculate_coverage(
    df: pd.DataFrame,
    template: ImportedTemplate,
) -> MigrationCoverage:
    """
    Calculate migration coverage from the source DataFrame
    and the mapped template.
    """

    sections = template.sections

    items = [
        item
        for section in sections
        for item in section.items
    ]

    fields = list(_flatten_fields(template))

    metadata_columns = 0
    photo_columns = 0

    if fields:
        metadata_keys = fields[0].source_metadata.keys()

        metadata_columns = len(
            fields[0].source_metadata
        )

        photo_columns = sum(
            1
            for key in metadata_keys
            if PHOTO_COLUMN_PATTERN.match(key)
        )

    html_rows = 0
    link_rows = 0
    populated_photos = 0

    for field in fields:
        comment = field.comment_text or ""

        if HTML_PATTERN.search(comment):
            html_rows += 1

        if LINK_PATTERN.search(comment):
            link_rows += 1

        for key, value in field.source_metadata.items():
            if PHOTO_COLUMN_PATTERN.match(key):
                if value not in (None, "", "nan"):
                    populated_photos += 1

    return MigrationCoverage(
        sections_imported=len(sections),
        items_imported=len(items),
        fields_imported=len(fields),
        metadata_columns_preserved=metadata_columns,
        html_rows_detected=html_rows,
        link_rows_detected=link_rows,
        photo_columns_detected=photo_columns,
        populated_photo_values=populated_photos,
    )
