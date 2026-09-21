from __future__ import annotations

from pathlib import Path

from app.schemas.template import ImportIssue, ImportResult
from app.services.importer.coverage import calculate_coverage
from app.services.importer.mapper import map_dataframe
from app.services.importer.reader import read_template_file
from app.services.importer.validator import validate_dataframe


def import_template(
    file_path: str | Path,
    template_name: str,
) -> ImportResult:
    """
    Execute the complete Spectora import pipeline:

    1. Read the spreadsheet
    2. Validate its structure/content
    3. Map valid rows into our domain model
    """

    path = Path(file_path)

    try:
        dataframe = read_template_file(path)
    except (FileNotFoundError, ValueError) as exc:
        return ImportResult(
            issues=[
                ImportIssue(
                    severity="error",
                    message=str(exc),
                )
            ]
        )

    rows_processed = len(dataframe)

    validation_issues = validate_dataframe(dataframe)

    if any(issue.severity == "error" for issue in validation_issues):
        return ImportResult(
            rows_processed=rows_processed,
            issues=[
                ImportIssue(
                    row=issue.row,
                    severity="error",
                    message=issue.message,
                )
                for issue in validation_issues
            ],
        )

    try:
        template = map_dataframe(
            dataframe,
            template_name=template_name,
            source_file=path.name,
        )
        coverage = calculate_coverage(
            dataframe,
            template,
        )
    except Exception as exc:
        return ImportResult(
            rows_processed=rows_processed,
            issues=[
                ImportIssue(
                    severity="error",
                    message=f"Mapping failed: {exc}",
                )
            ],
        )

    rows_imported = sum(
        len(item.fields)
        for section in template.sections
        for item in section.items
    )

    return ImportResult(
        template=template,
        rows_processed=rows_processed,
        rows_imported=rows_imported,
        coverage=coverage,
    )