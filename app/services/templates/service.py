from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.database.repository import save_template, duplicate_template
from app.schemas.template import ImportedTemplate


def persist_template(
    db: Session,
    imported_template: ImportedTemplate,
):
    """
    Save a complete imported template in one transaction.
    """

    try:
        template = save_template(
            db,
            imported_template,
        )

        db.commit()

        return template

    except Exception:
        db.rollback()
        raise

def duplicate_template_service(
    db: Session,
    template_id: UUID,
    new_name: str | None = None,
):
    """
    Duplicate a template in one database transaction.
    """

    try:
        template = duplicate_template(
            db,
            template_id,
            new_name=new_name,
        )

        if template is None:
            db.rollback()
            return None

        db.commit()
        db.refresh(template)

        return template

    except Exception:
        db.rollback()
        raise