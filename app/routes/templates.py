from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.repository import (
    get_template,
    get_templates,
    update_field_comment,
    update_item_name,
    update_section_name,
)
from app.services.rendering.html import sanitize_html
from app.services.templates.service import (
    duplicate_template_service,
)

router = APIRouter()

templates = Jinja2Templates(
    directory="app/web/templates"
)
templates.env.filters["sanitize_html"] = sanitize_html


@router.get(
    "/",
    response_class=HTMLResponse,
)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
):
    template_list = get_templates(db)

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "templates": template_list,
        },
    )


@router.get(
    "/templates/{template_id}",
    response_class=HTMLResponse,
)
def template_detail(
    template_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
):
    template = get_template(db, template_id)

    if template is None:
        raise HTTPException(
            status_code=404,
            detail="Template not found",
        )

    sections = template.sections

    items = [
        item
        for section in sections
        for item in section.items
    ]

    fields = [
        field
        for section in sections
        for item in section.items
        for field in item.fields
    ]

    return templates.TemplateResponse(
        request=request,
        name="template_detail.html",
        context={
            "template": template,
            "section_count": len(sections),
            "item_count": len(items),
            "field_count": len(fields),
        },
    )

@router.post("/sections/{section_id}/name")
def update_section(
    section_id: UUID,
    name: str = Form(...),
    db: Session = Depends(get_db),
):
    updated = update_section_name(
        db,
        section_id,
        name,
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Section not found",
        )

    return RedirectResponse(
        url=f"/templates/{updated.template_id}",
        status_code=303,
    )


@router.post("/items/{item_id}/name")
def update_item(
    item_id: UUID,
    name: str = Form(...),
    db: Session = Depends(get_db),
):
    updated = update_item_name(
        db,
        item_id,
        name,
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )

    return RedirectResponse(
        url=f"/templates/{updated.section.template_id}",
        status_code=303,
    )


@router.post("/fields/{field_id}/comment")
def update_field(
    field_id: UUID,
    comment_text: str | None = Form(None),
    db: Session = Depends(get_db),
):
    updated = update_field_comment(
        db,
        field_id,
        comment_text,
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Field not found",
        )

    return RedirectResponse(
        url=f"/templates/{updated.item.section.template_id}",
        status_code=303,
    )


@router.post("/templates/{template_id}/duplicate")
def duplicate_template_route(
    template_id: UUID,
    db: Session = Depends(get_db),
):
    copied = duplicate_template_service(
        db,
        template_id,
    )

    if copied is None:
        raise HTTPException(
            status_code=404,
            detail="Template not found",
        )

    return RedirectResponse(
        url=f"/templates/{copied.id}",
        status_code=303,
    )