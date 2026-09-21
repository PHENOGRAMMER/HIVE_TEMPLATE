from __future__ import annotations

import secrets
from collections import Counter
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Request,
    UploadFile,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.importer.service import import_template
from app.services.templates.service import persist_template


router = APIRouter()

templates = Jinja2Templates(
    directory="app/web/templates"
)

ALLOWED_EXTENSIONS = {".xls", ".xlsx"}


# Temporary in-memory storage for import previews.
#
# token -> ImportResult
#
# This is appropriate for the take-home's single-process
# workflow. We can replace it with persistent staging later
# if needed.
_preview_store = {}


@router.get(
    "/import",
    response_class=HTMLResponse,
)
def import_page(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="import.html",
        context={},
    )


@router.post(
    "/import/preview",
    response_class=HTMLResponse,
)
async def import_preview(
    request: Request,
    file: UploadFile = File(...),
    template_name: str = Form(...),
):
    """
    Parse and validate the uploaded template without
    persisting it yet.
    """

    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return templates.TemplateResponse(
            request=request,
            name="import.html",
            context={
                "error": (
                    "Unsupported file type. "
                    "Please upload an .xls or .xlsx file."
                )
            },
            status_code=400,
        )

    with NamedTemporaryFile(
        delete=False,
        suffix=extension,
    ) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = Path(temp_file.name)

    try:
        result = import_template(
            temp_path,
            template_name=template_name,
        )

        if not result.successful:
            return templates.TemplateResponse(
                request=request,
                name="import.html",
                context={
                    "error": (
                        "This doesn't appear to be a valid "
                        "Spectora export."
                    ),
                    "issues": result.issues,
                },
                status_code=400,
            )

        # Preserve the user's actual uploaded filename.
        result.template.source_file = filename

        token = secrets.token_urlsafe(24)

        _preview_store[token] = result

        # Calculate preview statistics.
        sections = result.template.sections

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

        answer_type_counts = Counter(
            field.answer_type
            for field in fields
        )

        comment_type_counts = Counter(
            field.comment_type
            for field in fields
        )

        return templates.TemplateResponse(
            request=request,
            name="import_preview.html",
            context={
                "template": result.template,
                "token": token,
                "rows_processed": result.rows_processed,
                "rows_imported": result.rows_imported,
                "section_count": len(sections),
                "item_count": len(items),
                "field_count": len(fields),
                "answer_type_counts": answer_type_counts,
                "comment_type_counts": comment_type_counts,
                "issues": result.issues,
                "coverage": result.coverage,
            },
        )

    finally:
        temp_path.unlink(missing_ok=True)


@router.post(
    "/import/confirm",
)
def confirm_import(
    token: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Persist an import that the user already reviewed.
    """

    result = _preview_store.get(token)

    if result is None:
        return HTMLResponse(
            content=(
                "<h1>Preview expired</h1>"
                "<p>Please upload the template again.</p>"
            ),
            status_code=410,
        )

    if not result.successful or result.template is None:
        return HTMLResponse(
            content="<h1>Import is not valid.</h1>",
            status_code=400,
        )

    try:
        saved_template = persist_template(
            db,
            result.template,
        )

        # Remove preview after successful persistence.
        _preview_store.pop(token, None)

        return RedirectResponse(
            url=f"/templates/{saved_template.id}",
            status_code=303,
        )

    except Exception:
        db.rollback()
        raise