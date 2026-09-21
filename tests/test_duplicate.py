from app.database.connection import SessionLocal
from app.database.repository import get_template
from app.database.models import Template
from app.services.importer.mapper import map_dataframe
from app.services.importer.reader import read_template_file
from app.services.templates.service import (
    duplicate_template_service,
)
from app.services.templates.service import persist_template


FILE_PATH = (
    "data/fixtures/"
    "InterNACHI Residential -2026-09-20.xlsx"
)


def test_duplicate_template_is_independent():
    df = read_template_file(FILE_PATH)

    imported_template = map_dataframe(
        df,
        template_name="Duplication Test Template",
        source_file="InterNACHI Residential -2026-09-20.xlsx",
    )

    db = SessionLocal()

    original_id = None
    copy_id = None

    try:
        original = persist_template(
            db,
            imported_template,
        )

        original_id = original.id

        copied = duplicate_template_service(
            db,
            original.id,
            new_name="Duplication Test Template Copy",
        )

        assert copied is not None

        copy_id = copied.id

        assert copy_id != original_id

        original_loaded = get_template(
            db,
            original_id,
        )

        copy_loaded = get_template(
            db,
            copy_id,
        )

        assert original_loaded is not None
        assert copy_loaded is not None

        assert (
            original_loaded.name
            == "Duplication Test Template"
        )

        assert (
            copy_loaded.name
            == "Duplication Test Template Copy"
        )

        # Both templates should have the same initial structure.
        assert len(original_loaded.sections) == len(
            copy_loaded.sections
        )

        assert len(
            original_loaded.sections[0].items
        ) == len(
            copy_loaded.sections[0].items
        )

        original_item = (
            original_loaded
            .sections[0]
            .items[0]
        )

        copied_item = (
            copy_loaded
            .sections[0]
            .items[0]
        )

        assert original_item.id != copied_item.id

    finally:
        # Delete copy first.
        if copy_id is not None:
            copied = db.get(
                Template,
                copy_id,
            )

            if copied is not None:
                db.delete(copied)
                db.commit()

        if original_id is not None:
            original = db.get(
                Template,
                original_id,
            )

            if original is not None:
                db.delete(original)
                db.commit()

        db.close()


def test_editing_copy_does_not_change_original():
    df = read_template_file(FILE_PATH)

    imported_template = map_dataframe(
        df,
        template_name="Independent Copy Test",
        source_file="InterNACHI Residential -2026-09-20.xlsx",
    )

    db = SessionLocal()

    original_id = None
    copy_id = None

    try:
        original = persist_template(
            db,
            imported_template,
        )

        original_id = original.id

        copied = duplicate_template_service(
            db,
            original.id,
            new_name="Independent Copy Test Copy",
        )

        assert copied is not None

        copy_id = copied.id

        original_section_name = (
            original.sections[0].name
        )

        copied.sections[0].name = (
            "Changed Only In Copy"
        )

        db.commit()

        original_loaded = get_template(
            db,
            original_id,
        )

        copy_loaded = get_template(
            db,
            copy_id,
        )

        assert original_loaded is not None
        assert copy_loaded is not None

        assert (
            original_loaded.sections[0].name
            == original_section_name
        )

        assert (
            copy_loaded.sections[0].name
            == "Changed Only In Copy"
        )

    finally:
        if copy_id is not None:
            copied = db.get(
                Template,
                copy_id,
            )

            if copied is not None:
                db.delete(copied)
                db.commit()

        if original_id is not None:
            original = db.get(
                Template,
                original_id,
            )

            if original is not None:
                db.delete(original)
                db.commit()

        db.close()