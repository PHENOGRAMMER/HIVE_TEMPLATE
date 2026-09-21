from sqlalchemy import select

from app.database.connection import SessionLocal
from app.database.models import Item, Section, Template, TemplateField
from app.services.importer.mapper import map_dataframe
from app.services.importer.reader import read_template_file
from app.services.templates.service import persist_template


FILE_PATH = (
    "data/fixtures/"
    "InterNACHI Residential -2026-09-20.xlsx"
)


def test_real_template_persists_to_database():
    df = read_template_file(FILE_PATH)

    imported_template = map_dataframe(
        df,
        template_name="InterNACHI Residential",
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

        saved_template = db.scalar(
            select(Template).where(
                Template.id == template_id
            )
        )

        assert saved_template is not None
        assert saved_template.name == "InterNACHI Residential"

        sections = db.scalars(
            select(Section)
            .where(Section.template_id == template_id)
            .order_by(Section.position)
        ).all()

        assert len(sections) > 0

        items = db.scalars(
            select(Item)
            .join(Section)
            .where(Section.template_id == template_id)
        ).all()

        assert len(items) > 0

        fields = db.scalars(
            select(TemplateField)
            .join(Item)
            .join(Section)
            .where(Section.template_id == template_id)
        ).all()

        assert len(fields) == 392

    finally:
        if template_id is not None:
            template = db.get(Template, template_id)

            if template is not None:
                db.delete(template)
                db.commit()

        db.close()