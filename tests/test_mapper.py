from app.schemas.template import ImportedTemplate
from app.services.importer.mapper import map_dataframe
from app.services.importer.reader import read_template_file


FILE_PATH = (
    "data/fixtures/"
    "InterNACHI Residential -2026-09-20.xlsx"
)


def test_real_fixture_maps_to_template():
    df = read_template_file(FILE_PATH)

    template = map_dataframe(
        df,
        template_name="InterNACHI Residential",
        source_file="InterNACHI Residential -2026-09-20.xlsx",
    )

    assert isinstance(template, ImportedTemplate)

    assert template.name == "InterNACHI Residential"
    assert template.source == "Spectora"

    # The source has 392 spreadsheet rows, so we should get
    # exactly 392 imported fields.
    fields = [
        field
        for section in template.sections
        for item in section.items
        for field in item.fields
    ]

    assert len(fields) == 392


def test_real_fixture_maps_defect_field():
    df = read_template_file(FILE_PATH)

    template = map_dataframe(
        df,
        template_name="InterNACHI Residential",
        source_file="InterNACHI Residential -2026-09-20.xlsx",
    )

    fields = [
        field
        for section in template.sections
        for item in section.items
        for field in item.fields
    ]

    defect = next(
        field
        for field in fields
        if field.name == "Cracking - Major"
    )

    assert defect.comment_type == "defect"
    assert defect.answer_type == "boolean"
    assert defect.category == 0
    assert defect.source_row == 10


def test_real_fixture_preserves_unmapped_source_metadata():
    df = read_template_file(FILE_PATH)

    template = map_dataframe(
        df,
        template_name="InterNACHI Residential",
        source_file="InterNACHI Residential -2026-09-20.xlsx",
    )

    fields = [
        field
        for section in template.sections
        for item in section.items
        for field in item.fields
    ]

    first_field = fields[0]

    assert "Default Photo 1" in first_field.source_metadata
    assert "Last Modified" in first_field.source_metadata

def test_real_fixture_preserves_multiple_choice_options():
    df = read_template_file(FILE_PATH)

    template = map_dataframe(
        df,
        template_name="InterNACHI Residential",
        source_file="InterNACHI Residential -2026-09-20.xlsx",
    )

    fields = [
        field
        for section in template.sections
        for item in section.items
        for field in item.fields
    ]

    field = next(
        field
        for field in fields
        if field.name == "In Attendance"
    )

    assert field.answer_type == "checkbox"

    assert field.options == [
        "Home Owner",
        "Client",
        "Client's Agent",
        "Listing Agent",
    ]