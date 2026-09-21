from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


REQUIRED_COLUMNS = {
    "Section Name",
    "Item Name",
    "Comment Name",
    "Comment Text",
    "Comment Type (info, limit, defect)",
    "Category (-1: Low, 0: Med, 1: High)",
    "Multiple Choice Options (comma-separated)",
    "Unit Type Options (numeric answers only, comma-separated)",
    "Recommendation (from list)",
    "Order (w/i item)",
    "Answer Type (boolean, checkbox, date, number, range, text)",
    "Default Value",
    "Default Value 2 (for \"range\" types)",
    "Default Unit Type (for \"number\" and \"range\" types)",
    "Default Location",
    "Default Estimate Min",
    "Default Estimate Max",
    "Locked",
    "Simple Format",
    "Disable Photos",
    "Uses",
    "Last Modified",
}


VALID_COMMENT_TYPES = {"info", "limit", "defect"}

VALID_ANSWER_TYPES = {
    "boolean",
    "checkbox",
    "date",
    "number",
    "range",
    "text",
}


@dataclass
class ValidationIssue:
    row: int | None
    severity: str
    message: str


def validate_columns(df: pd.DataFrame) -> list[ValidationIssue]:
    """
    Validate that the spreadsheet contains the columns
    required to interpret the template.
    """
    issues: list[ValidationIssue] = []

    missing = REQUIRED_COLUMNS - set(df.columns)

    for column in sorted(missing):
        issues.append(
            ValidationIssue(
                row=None,
                severity="error",
                message=f"Missing required column: {column}",
            )
        )

    return issues


def validate_rows(df: pd.DataFrame) -> list[ValidationIssue]:
    """
    Validate individual template rows.
    """
    issues: list[ValidationIssue] = []

    comment_type_column = "Comment Type (info, limit, defect)"
    answer_type_column = (
        "Answer Type (boolean, checkbox, date, number, range, text)"
    )

    for index, row in df.iterrows():
        source_row = index + 2  # Excel header is row 1.

        section = row.get("Section Name")
        item = row.get("Item Name")
        comment_name = row.get("Comment Name")
        comment_type = row.get(comment_type_column)
        answer_type = row.get(answer_type_column)

        if pd.isna(section) or not str(section).strip():
            issues.append(
                ValidationIssue(
                    row=source_row,
                    severity="error",
                    message="Section Name is empty.",
                )
            )

        if pd.isna(item) or not str(item).strip():
            issues.append(
                ValidationIssue(
                    row=source_row,
                    severity="error",
                    message="Item Name is empty.",
                )
            )

        if pd.isna(comment_name) or not str(comment_name).strip():
            issues.append(
                ValidationIssue(
                    row=source_row,
                    severity="error",
                    message="Comment Name is empty.",
                )
            )

        if not pd.isna(comment_type):
            normalized_comment_type = str(comment_type).strip().lower()

            if normalized_comment_type not in VALID_COMMENT_TYPES:
                issues.append(
                    ValidationIssue(
                        row=source_row,
                        severity="error",
                        message=(
                            f"Unsupported comment type: "
                            f"{comment_type}"
                        ),
                    )
                )

        if not pd.isna(answer_type):
            normalized_answer_type = str(answer_type).strip().lower()

            if normalized_answer_type not in VALID_ANSWER_TYPES:
                issues.append(
                    ValidationIssue(
                        row=source_row,
                        severity="error",
                        message=(
                            f"Unsupported answer type: "
                            f"{answer_type}"
                        ),
                    )
                )

    return issues


def validate_dataframe(df: pd.DataFrame) -> list[ValidationIssue]:
    """
    Run all validation checks.

    Column validation is performed first because row validation
    depends on those columns existing.
    """
    issues = validate_columns(df)

    if any(issue.severity == "error" for issue in issues):
        return issues

    issues.extend(validate_rows(df))

    return issues