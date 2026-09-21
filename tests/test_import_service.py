from app.services.importer.service import import_template


FILE_PATH = (
    "data/fixtures/"
    "InterNACHI Residential -2026-09-20.xlsx"
)


def test_import_service_imports_real_fixture():
    result = import_template(
        FILE_PATH,
        template_name="InterNACHI Residential",
    )

    assert result.successful is True
    assert result.rows_processed == 392
    assert result.rows_imported == 392

    assert len(result.errors) == 0

def test_import_service_rejects_missing_file():
    result = import_template(
        "data/fixtures/does-not-exist.xlsx",
        template_name="Invalid",
    )

    assert result.successful is False
    assert len(result.errors) == 1


def test_import_service_rejects_invalid_spectora_file():
    result = import_template(
        "data/fixtures/invalid-spectora.xlsx",
        template_name="Invalid",
    )

    assert result.successful is False
    assert result.template is None
    assert result.errors
    assert all(issue.row is None for issue in result.errors)
    assert any(
        issue.message == "Missing required column: Section Name"
        for issue in result.errors
    )