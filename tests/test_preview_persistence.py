from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.database.connection import SessionLocal
from app.database.models import Template

client = TestClient(app)

FIXTURE = Path(
    "data/fixtures/InterNACHI Residential -2026-09-20.xlsx"
)


def test_import_preview_does_not_persist_template():
    db = SessionLocal()

    try:
        before_count = db.query(Template).count()

        with FIXTURE.open("rb") as file:
            response = client.post(
                "/import/preview",
                data={
                    "template_name": "Preview Only Test",
                },
                files={
                    "file": (
                        FIXTURE.name,
                        file,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                },
            )

        assert response.status_code == 200
        assert "Import Preview" in response.text
        assert "Ready to import" in response.text

        db.expire_all()

        after_count = db.query(Template).count()

        assert after_count == before_count

    finally:
        db.close()