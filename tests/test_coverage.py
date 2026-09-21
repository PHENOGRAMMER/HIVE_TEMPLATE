from app.services.importer.coverage import calculate_coverage
from app.services.importer.mapper import map_dataframe
from app.services.importer.reader import read_template_file


FILE_PATH = (
    "data/fixtures/"
    "InterNACHI Residential -2026-09-20.xlsx"
)


def test_real_fixture_has_migration_coverage():
    df = read_template_file(FILE_PATH)

    template = map_dataframe(
        df,
        template_name="InterNACHI Residential",
        source_file="InterNACHI Residential -2026-09-20.xlsx",
    )

    coverage = calculate_coverage(
        df,
        template,
    )

    assert coverage.sections_imported == 13
    assert coverage.fields_imported == 392

    assert coverage.metadata_columns_preserved > 0

    assert coverage.html_rows_detected > 0
    assert coverage.link_rows_detected > 0

    assert coverage.photo_columns_detected == 10
    assert coverage.populated_photo_values == 0
