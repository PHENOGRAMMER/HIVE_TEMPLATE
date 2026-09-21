from app.database.connection import SessionLocal
from app.database.models import Section, Template, TemplateField
from app.database.repository import (
    get_template,
    update_field_comment,
    update_item_name,
    update_section_name,
)
from app.services.importer.mapper import map_dataframe
from app.services.importer.reader import read_template_file
from app.services.templates.service import persist_template


FILE_PATH = (
    "data/fixtures/"
    "InterNACHI Residential -2026-09-20.xlsx"
)


def test_get_template_loads_complete_hierarchy():
    df = read_template_file(FILE_PATH)

    imported_template = map_dataframe(
        df,
        template_name="Repository Test Template",
        source_file="InterNACHI Residential -2026-09-20.xlsx",
    )

    db = SessionLocal()

    template_id = None

    try:
        template = persist_template(
            db,
            imported_template,
        )

        template_id = template.id

        loaded = get_template(
            db,
            template_id,
        )

        assert loaded is not None
        assert loaded.name == "Repository Test Template"

        assert len(loaded.sections) > 0
        assert len(loaded.sections[0].items) > 0
        assert len(loaded.sections[0].items[0].fields) > 0

    finally:
        if template_id is not None:
            template = db.get(Template, template_id)

            if template is not None:
                db.delete(template)
                db.commit()

        db.close()


def test_update_section_name():
    df = read_template_file(FILE_PATH)

    imported_template = map_dataframe(
        df,
        template_name="Edit Test Template",
        source_file="InterNACHI Residential -2026-09-20.xlsx",
    )

    db = SessionLocal()

    template_id = None

    try:
        template = persist_template(
            db,
            imported_template,
        )

        template_id = template.id

        section = template.sections[0]

        original_name = section.name
        new_name = f"{original_name} - Edited"

        updated = update_section_name(
            db,
            section.id,
            new_name,
        )

        assert updated is not None
        assert updated.name == new_name

        loaded = get_template(
            db,
            template_id,
        )

        assert loaded is not None
        assert loaded.sections[0].name == new_name

    finally:
        if template_id is not None:
            template = db.get(Template, template_id)

            if template is not None:
                db.delete(template)
                db.commit()

        db.close()


def test_update_field_comment():
    df = read_template_file(FILE_PATH)

    imported_template = map_dataframe(
        df,
        template_name="Comment Test Template",
        source_file="InterNACHI Residential -2026-09-20.xlsx",
    )

    db = SessionLocal()

    template_id = None

    try:
        template = persist_template(
            db,
            imported_template,
        )

        template_id = template.id

        field = template.sections[1].items[1].fields[0]

        updated_text = "Updated comment from repository test."

        updated = update_field_comment(
            db,
            field.id,
            updated_text,
        )

        assert updated is not None
        assert updated.comment_text == updated_text

        loaded = get_template(
            db,
            template_id,
        )

        assert loaded is not None

        loaded_field = (
            loaded.sections[1]
            .items[1]
            .fields[0]
        )

        assert loaded_field.comment_text == updated_text

    finally:
        if template_id is not None:
            template = db.get(Template, template_id)

            if template is not None:
                db.delete(template)
                db.commit()

        db.close()

def test_update_item_name():
    df = read_template_file(FILE_PATH)

    imported_template = map_dataframe(
        df,
        template_name="Item Edit Test Template",
        source_file="InterNACHI Residential -2026-09-20.xlsx",
    )

    db = SessionLocal()

    template_id = None

    try:
        template = persist_template(
            db,
            imported_template,
        )

        template_id = template.id

        item = template.sections[0].items[0]

        original_name = item.name
        new_name = f"{original_name} - Edited"

        updated = update_item_name(
            db,
            item.id,
            new_name,
        )

        assert updated is not None
        assert updated.name == new_name

        loaded = get_template(
            db,
            template_id,
        )

        assert loaded is not None
        assert loaded.sections[0].items[0].name == new_name

    finally:
        if template_id is not None:
            template = db.get(Template, template_id)

            if template is not None:
                db.delete(template)
                db.commit()

        db.close()