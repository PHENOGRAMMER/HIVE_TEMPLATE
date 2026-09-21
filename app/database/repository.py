from __future__ import annotations

from uuid import UUID

from copy import deepcopy

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database.models import (
    Item,
    Section,
    Template,
    TemplateField,
)
from app.schemas.template import ImportedTemplate


def save_template(
    db: Session,
    imported_template: ImportedTemplate,
) -> Template:
    """
    Persist an ImportedTemplate and its complete hierarchy.

    The caller is responsible for committing/rolling back the
    transaction.
    """

    template = Template(
        name=imported_template.name,
        source=imported_template.source,
        source_file=imported_template.source_file,
    )

    db.add(template)
    db.flush()

    for imported_section in imported_template.sections:
        section = Section(
            template_id=template.id,
            name=imported_section.name,
            position=imported_section.position,
        )

        db.add(section)
        db.flush()

        for imported_item in imported_section.items:
            item = Item(
                section_id=section.id,
                name=imported_item.name,
                position=imported_item.position,
            )

            db.add(item)
            db.flush()

            for position, imported_field in enumerate(
                imported_item.fields
            ):
                field = TemplateField(
                    item_id=item.id,
                    name=imported_field.name,
                    comment_text=imported_field.comment_text,
                    comment_type=imported_field.comment_type,
                    category=imported_field.category,
                    answer_type=imported_field.answer_type,
                    options=imported_field.options,
                    unit_options=imported_field.unit_options,
                    recommendation=imported_field.recommendation,
                    position=position,
                    source_order=imported_field.order,
                    default_value=imported_field.default_value,
                    default_value_2=imported_field.default_value_2,
                    default_unit_type=(
                        imported_field.default_unit_type
                    ),
                    default_location=(
                        imported_field.default_location
                    ),
                    estimate_min=imported_field.estimate_min,
                    estimate_max=imported_field.estimate_max,
                    locked=imported_field.locked,
                    simple_format=imported_field.simple_format,
                    disable_photos=imported_field.disable_photos,
                    uses=imported_field.uses,
                    source_row=imported_field.source_row,
                )

                db.add(field)

    return template


def get_template(
    db: Session,
    template_id: UUID,
) -> Template | None:
    """
    Retrieve a template with its complete hierarchy:

    Template
        -> Sections
            -> Items
                -> Fields
    """

    statement = (
        select(Template)
        .where(Template.id == template_id)
        .options(
            selectinload(Template.sections)
            .selectinload(Section.items)
            .selectinload(Item.fields)
        )
    )

    return db.scalar(statement)


def update_section_name(
    db: Session,
    section_id: UUID,
    new_name: str,
) -> Section | None:
    """
    Update a section's name.
    """

    section = db.get(Section, section_id)

    if section is None:
        return None

    cleaned_name = new_name.strip()

    if not cleaned_name:
        raise ValueError("Section name cannot be empty.")

    section.name = cleaned_name

    db.commit()
    db.refresh(section)

    return section


def update_item_name(
    db: Session,
    item_id: UUID,
    new_name: str,
) -> Item | None:
    """
    Update an item's name.
    """

    item = db.get(Item, item_id)

    if item is None:
        return None

    cleaned_name = new_name.strip()

    if not cleaned_name:
        raise ValueError("Item name cannot be empty.")

    item.name = cleaned_name

    db.commit()
    db.refresh(item)

    return item


def update_field_comment(
    db: Session,
    field_id: UUID,
    comment_text: str | None,
) -> TemplateField | None:
    """
    Update the comment text associated with a template field.
    """

    field = db.get(TemplateField, field_id)

    if field is None:
        return None

    field.comment_text = comment_text

    db.commit()
    db.refresh(field)

    return field


def duplicate_template(
    db: Session,
    template_id: UUID,
    new_name: str | None = None,
) -> Template | None:
    """
    Create a completely independent copy of a template,
    including all sections, items, and fields.

    The caller is responsible for committing/rolling back.
    """

    original = get_template(
        db,
        template_id,
    )

    if original is None:
        return None

    copied_template = Template(
        name=new_name or f"{original.name} (Copy)",
        source=original.source,
        source_file=original.source_file,
    )

    db.add(copied_template)
    db.flush()

    for original_section in original.sections:
        copied_section = Section(
            template_id=copied_template.id,
            name=original_section.name,
            position=original_section.position,
        )

        db.add(copied_section)
        db.flush()

        for original_item in original_section.items:
            copied_item = Item(
                section_id=copied_section.id,
                name=original_item.name,
                position=original_item.position,
            )

            db.add(copied_item)
            db.flush()

            for original_field in original_item.fields:
                copied_field = TemplateField(
                    item_id=copied_item.id,
                    name=original_field.name,
                    comment_text=original_field.comment_text,
                    comment_type=original_field.comment_type,
                    category=original_field.category,
                    answer_type=original_field.answer_type,
                    options=deepcopy(original_field.options),
                    unit_options=deepcopy(
                        original_field.unit_options
                    ),
                    recommendation=original_field.recommendation,
                    position=original_field.position,
                    source_order=original_field.source_order,
                    default_value=deepcopy(
                        original_field.default_value
                    ),
                    default_value_2=deepcopy(
                        original_field.default_value_2
                    ),
                    default_unit_type=(
                        original_field.default_unit_type
                    ),
                    default_location=original_field.default_location,
                    estimate_min=original_field.estimate_min,
                    estimate_max=original_field.estimate_max,
                    locked=original_field.locked,
                    simple_format=original_field.simple_format,
                    disable_photos=original_field.disable_photos,
                    uses=original_field.uses,
                    source_row=original_field.source_row,
                    source_metadata=deepcopy(
                        original_field.source_metadata
                    ),
                )

                db.add(copied_field)

    return copied_template

def get_templates(
    db: Session,
) -> list[Template]:
    """
    Return all templates, newest first.
    """
    statement = (
        select(Template)
        .order_by(Template.created_at.desc())
    )

    return list(db.scalars(statement).all())