# Hive Template Importer

A Python/FastAPI application for importing Spectora XLSX inspection templates into a normalized, editable template structure backed by PostgreSQL/Supabase.

The project was developed as a take-home assignment for a Forward Deployed Engineer role.

## Overview

The application accepts a Spectora template export in XLSX format and converts it into a normalized hierarchy:

```text
Template
└── Sections
    └── Items
        └── Fields
```

The application provides:

- Spectora XLSX upload
- Source validation
- Migration preview before persistence
- Normalized template hierarchy
- Migration coverage information
- Preservation of additional source metadata
- HTML-rich comment preservation and safe rendering
- Section editing
- Item editing
- Field comment editing
- Independent template duplication
- Failure handling for invalid imports
- PostgreSQL/Supabase persistence
- Automated tests

---

## Technology Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Jinja2

### Database

- PostgreSQL
- Supabase

### Import Processing

- Pandas
- OpenPyXL

### Security

- Bleach HTML sanitization

### Testing

- Pytest
- FastAPI TestClient

---

## Architecture

The application is organized into several layers.

```text
app/
├── config.py
├── main.py
│
├── database/
│   ├── connection.py
│   ├── models.py
│   └── repository.py
│
├── routes/
│   ├── imports.py
│   └── templates.py
│
├── schemas/
│   └── template.py
│
├── services/
│   ├── importer/
│   │   ├── reader.py
│   │   ├── validator.py
│   │   ├── mapper.py
│   │   ├── coverage.py
│   │   └── service.py
│   │
│   ├── rendering/
│   │   └── html.py
│   │
│   └── templates/
│       └── service.py
│
└── web/
    ├── static/
    └── templates/
```

---

## Import Pipeline

The import process is intentionally separated into stages:

```text
Spectora XLSX
      │
      ▼
   Reader
      │
      ▼
  Validator
      │
      ▼
    Mapper
      │
      ▼
Coverage Analysis
      │
      ▼
 Import Preview
      │
      ▼
 Confirm Import
      │
      ▼
 PostgreSQL
```

This separation allows validation and preview to happen before database persistence.

---

## Normalized Data Model

The imported template is represented using a normalized hierarchy.

```text
Template
│
├── Section
│   │
│   ├── Item
│   │   │
│   │   ├── Field
│   │   ├── Field
│   │   └── ...
│   │
│   └── ...
│
└── ...
```

A field stores information such as:

- Field name
- Answer type
- Comment type
- Comment text
- Multiple-choice options
- Source metadata

The relationships are persisted using SQLAlchemy and PostgreSQL.

---

## Source Data Handling

The importer treats the Spectora XLSX export as the source format.

The importer validates required source columns before attempting persistence.

The migration preview reports:

- Rows processed
- Sections
- Items
- Fields
- Answer types
- Comment types
- Additional metadata
- HTML-containing rows
- Rows containing links
- Default photo columns
- Populated default photos

This makes the migration behavior visible before confirming the template.

---

## Rich HTML Content

Spectora comments may contain HTML formatting and links.

The importer preserves the comment content rather than stripping HTML during migration.

HTML is sanitized at the rendering boundary using Bleach.

Supported content includes common formatting such as:

- Paragraphs
- Line breaks
- Bold
- Italic
- Underline
- Ordered lists
- Unordered lists
- Links

Links are restricted to supported protocols such as:

- `http`
- `https`
- `mailto`

Dangerous HTML and tested JavaScript URL cases are sanitized before rendering.

---

## Source Metadata Preservation

Not every source column maps directly to a normalized field.

Instead of silently discarding unmapped information, additional source metadata is retained on imported fields.

This provides a way to preserve information that may be useful for future migration work while keeping the primary application model normalized.

---

## Preview Before Persistence

The import flow separates preview from database persistence.

The preview allows the user to inspect the migration result before confirming the import.

A preview does not create a persistent template record.

Only the explicit confirmation step writes the imported hierarchy to PostgreSQL.

---

## Editing

Imported templates can be edited after persistence.

Supported edits include:

### Sections

- Rename a section

### Items

- Rename an item

### Fields

- Edit field comment text

Changes are persisted to PostgreSQL.

---

## Template Duplication

A persisted template can be duplicated.

The duplication creates an independent copy of:

- Template
- Sections
- Items
- Fields

The copied records receive their own identifiers.

Editing the duplicated template does not modify the original template.

This behavior is covered by automated tests.

---

## Failure Handling

The application validates the uploaded workbook before persistence.

For an invalid workbook, the application displays a clear import failure message identifying the missing or invalid source requirements.

The failed import does not create a template in the database.

This behavior is covered by automated tests and was also verified through the application UI.

---

## Testing

The project contains automated tests covering:

- XLSX validation
- Mapping
- Migration coverage
- Import service behavior
- Real Spectora fixture parsing
- Database persistence
- Repository operations
- Preview persistence behavior
- Template duplication
- Duplicate independence
- HTML sanitization
- Pydantic schemas

Run the test suite with:

```bash
python -m pytest
```

The final local test suite currently contains 23 passing tests.

---

## Local Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd HIVE_TEMPLATE
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg://postgres:<password>@<host>:5432/postgres
```

Do not commit the real `.env` file.

### 5. Create database tables

```bash
python create_tables.py
```

### 6. Start the application

```bash
uvicorn app.main:app --reload
```

The application will normally be available at:

```text
http://localhost:8000
```

---

## Application Flow

The primary workflow is:

```text
1. Open Import
2. Upload Spectora XLSX
3. Review migration preview
4. Inspect coverage and source metadata
5. Confirm import
6. Open imported template
7. Edit sections/items/comments
8. Duplicate template
9. Verify duplicate independence
```

---

## Environment Variables

The application requires:

```env
DATABASE_URL=
```

A sample configuration is provided in:

```text
.env.example
```

Credentials and secrets should never be committed to source control.

---

## Known Tradeoffs

### XLSX

The assignment workflow uses Spectora XLSX exports as the canonical input format.

### Preview Storage

Preview state is kept separately from persistent template records so that previewing an import does not mutate the database.

### Source Metadata

Source metadata is preserved where it does not map directly to the normalized application model.

### Rich Content

HTML is preserved during import and sanitized when rendered.

This avoids destroying source content while still preventing the application from rendering unsafe HTML.

---

## Project Status

The core migration workflow is implemented and tested:

- Import: complete
- Validation: complete
- Preview: complete
- Persistence: complete
- Editing: complete
- Duplication: complete
- HTML sanitization: complete
- Failure handling: complete
- Automated tests: complete
- Deployment: prepared separately
