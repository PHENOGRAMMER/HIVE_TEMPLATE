from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes.imports import router as import_router
from app.routes.templates import router as template_router


app = FastAPI(
    title="Hive FDE Template Importer",
    version="1.0.0",
)

static_directory = Path(__file__).resolve().parent / "web" / "static"

app.mount(
    "/static",
    StaticFiles(directory=static_directory),
    name="static",
)

app.include_router(template_router)
app.include_router(import_router)