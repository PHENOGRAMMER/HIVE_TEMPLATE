from app.services.importer.reader import read_template_file
from app.services.importer.validator import validate_dataframe


FILE_PATH = "data/fixtures/InterNACHI Residential -2026-09-20.xlsx"


def test_real_spectora_fixture_is_valid():
    df = read_template_file(FILE_PATH)

    issues = validate_dataframe(df)

    errors = [
        issue for issue in issues
        if issue.severity == "error"
    ]

    assert errors == []
    assert len(df) == 392