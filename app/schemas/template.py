from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


CommentType = Literal["info", "limit", "defect"]

AnswerType = Literal[
    "boolean",
    "checkbox",
    "date",
    "number",
    "range",
    "text",
]


class ImportedField(BaseModel):
    """
    Structured representation of one row from the Spectora export.
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    comment_text: str | None = None

    comment_type: CommentType
    category: int | None = None

    answer_type: AnswerType

    options: list[str] = Field(default_factory=list)
    unit_options: list[str] = Field(default_factory=list)

    recommendation: str | None = None

    order: int | None = None

    default_value: Any | None = None
    default_value_2: Any | None = None
    default_unit_type: str | None = None
    default_location: str | None = None

    estimate_min: float | None = None
    estimate_max: float | None = None

    locked: bool | None = None
    simple_format: bool | None = None
    disable_photos: bool | None = None

    uses: int | None = None

    source_row: int

    source_metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class ImportedItem(BaseModel):
    """
    An Item groups fields belonging to the same Spectora item.
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    position: int

    fields: list[ImportedField] = Field(default_factory=list)


class ImportedSection(BaseModel):
    """
    A top-level Spectora section.
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    position: int

    items: list[ImportedItem] = Field(default_factory=list)


class ImportedTemplate(BaseModel):
    """
    Complete structured representation of an imported template.
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    source: str
    source_file: str

    sections: list[ImportedSection] = Field(default_factory=list)


class ImportIssue(BaseModel):
    """
    A warning or informational message produced during import.
    """

    row: int | None = None
    severity: Literal["warning", "unsupported", "error"]
    message: str


class MigrationCoverage(BaseModel):
    """
    Summary of what the importer preserved from the source.
    """

    sections_imported: int = 0
    items_imported: int = 0
    fields_imported: int = 0

    metadata_columns_preserved: int = 0

    html_rows_detected: int = 0
    link_rows_detected: int = 0

    photo_columns_detected: int = 0
    populated_photo_values: int = 0


class ImportResult(BaseModel):
    """
    Result of importing one Spectora template.
    """

    template: ImportedTemplate | None = None

    rows_processed: int = 0
    rows_imported: int = 0

    coverage: MigrationCoverage = Field(
        default_factory=MigrationCoverage
    )

    issues: list[ImportIssue] = Field(default_factory=list)

    @property
    def errors(self) -> list[ImportIssue]:
        return [
            issue
            for issue in self.issues
            if issue.severity == "error"
        ]

    @property
    def warnings(self) -> list[ImportIssue]:
        return [
            issue
            for issue in self.issues
            if issue.severity == "warning"
        ]

    @property
    def unsupported(self) -> list[ImportIssue]:
        return [
            issue
            for issue in self.issues
            if issue.severity == "unsupported"
        ]

    @property
    def successful(self) -> bool:
        return not self.errors and self.template is not None