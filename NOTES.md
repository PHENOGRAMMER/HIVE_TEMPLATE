# Engineering Notes

## Project

Hive Template Importer

This project implements a Spectora XLSX template migration workflow for the Hive FDE assignment.

The application imports a Spectora template export, converts it into a normalized hierarchy, previews the migration, persists the result to PostgreSQL, and allows the resulting template to be edited and duplicated.

The implementation prioritizes correctness, transparency of the migration, source-data preservation, and safe handling of rich content.

---

## 1. Source Format

The implementation uses the Spectora XLSX export as the canonical source format.

The workbook is read using OpenPyXL/Pandas.

The importer is organized into separate parsing, validation, mapping, coverage, and persistence stages instead of treating the workbook as a single opaque document.

---

## 2. Import Pipeline

The import pipeline is:

```text
Spectora XLSX
      |
      v
    Reader
      |
      v
   Validator
      |
      v
     Mapper
      |
      v
Coverage Analysis
      |
      v
 Import Preview
      |
      v
 Confirm Import
      |
      v
 PostgreSQL
```

Each stage has a specific responsibility.

### Reader

Loads the workbook into a tabular representation.

### Validator

Checks that required source columns exist and reports validation problems before persistence.

### Mapper

Transforms source rows into the normalized application model.

### Coverage Analysis

Calculates migration statistics and identifies source information such as HTML, links, photos, and additional metadata.

### Preview

Displays the mapped result and migration statistics without creating a persistent template.

### Persistence

Writes the confirmed template hierarchy to PostgreSQL.

---

## 3. Validation

The validator checks that the uploaded workbook contains the required Spectora columns.

If required columns are missing, the import fails before persistence.

The UI reports the validation problem to the user.

No template is created in the database when validation fails.

This provides a clear failure boundary:

```text
Invalid Input
     ↓
Validation Failure
     ↓
No Database Mutation
```

---

## 4. Normalized Model

The primary normalized hierarchy is:

```text
Template
└── Section
    └── Item
        └── Field
```

The database uses SQLAlchemy models backed by PostgreSQL.

This structure was chosen so that individual sections, items, and fields can be addressed and modified independently.

A field stores information such as:

- Field name
- Answer type
- Comment type
- Comment text
- Options
- Additional source metadata

---

## 5. Migration Mapping

The mapper converts source rows into the application hierarchy:

```text
Workbook rows
     |
     v
Sections
     |
     v
Items
     |
     v
Fields
```

The mapper also normalizes display text where appropriate.

HTML entities in section/item names are decoded for display. For example:

```text
&amp;
```

is displayed as:

```text
&
```

Comment content is handled differently because comments may contain meaningful HTML formatting and links.

Comment HTML is preserved during import and sanitized at rendering time.

---

## 6. Real Fixture Results

The real Spectora fixture used during development produced:

```text
Rows processed: 392
Sections:        13
Items:           69
Fields:          392
```

Answer types observed:

```text
boolean: 315
checkbox: 72
number:    4
text:      1
```

Comment types observed:

```text
defect: 302
info:    78
limit:   12
```

The migration preview also reports:

- Rows containing HTML
- Rows containing links
- Additional source metadata columns
- Default photo columns
- Populated default photo values

For the tested fixture:

```text
Rows containing HTML: 198
Rows containing links: 42
Additional metadata columns: 21
Default photo columns: 10
Populated default photos: 0
```

These statistics are shown in the preview to make migration behavior visible before persistence.

---

## 7. Migration Coverage

The importer distinguishes between data that is directly mapped into the normalized model and information that is preserved separately.

The preview reports:

```text
Imported
  Sections
  Items
  Fields

Preserved Source Metadata
  Additional metadata columns

Rich Content Detected
  HTML-containing rows
  Link-containing rows

Photos
  Default photo columns
  Populated default photos
```

This prevents a successful import from being interpreted as meaning that every source column has been directly represented in the normalized model.

---

## 8. Source Metadata Preservation

Not every Spectora source column has a direct equivalent in the application model.

Instead of silently discarding all unmapped information, additional source values are retained as source metadata where appropriate.

This approach allows the primary model to remain normalized while preserving information that may be relevant to future migration work.

---

## 9. Rich HTML Content

Spectora comments may contain HTML formatting and links.

The implementation deliberately preserves the source comment content instead of converting everything to plain text during import.

The security boundary is the rendering layer.

Before comment HTML is rendered in the application, it passes through an HTML sanitizer.

The sanitizer permits common formatting and supported links while restricting unsafe tags, attributes, and protocols.

The implementation includes tests for:

- Formatting
- Links
- Script content
- JavaScript URL cases

This allows useful rich content to remain visible without rendering untrusted HTML directly.

---

## 10. Preview vs Persistence

Previewing an import must not mutate the database.

The application therefore separates:

```text
Preview
```

from:

```text
Confirm Import
```

The preview is generated from the parsed and mapped data.

Only the explicit confirmation step creates the persistent template.

This behavior was tested by verifying that previewing an import does not create a template record in the database.

---

## 11. Persistence

The persistence layer is separated from the import transformation logic.

The repository layer handles operations such as:

- Creating templates
- Loading templates
- Updating sections
- Updating items
- Updating field comments

The template hierarchy is loaded together for the detail view so that the complete structure can be rendered efficiently.

---

## 12. Editing

The application supports persisted editing at three levels.

### Section

Rename a section.

### Item

Rename an item.

### Field

Edit field comment text.

The changes are written back to PostgreSQL.

---

## 13. Template Duplication

A persisted template can be duplicated.

Duplication creates a separate template hierarchy containing independent copies of:

```text
Template
Sections
Items
Fields
```

The duplicated records receive their own database identifiers.

The intended behavior is:

```text
Original Template
        |
        | duplicate
        v
Independent Copy
```

Changes to the copy do not affect the original.

This behavior is covered by automated tests.

---

## 14. Failure Handling

An intentionally invalid XLSX workbook was used to test the failure path.

The workbook was missing required source columns.

The application responded with an import failure instead of creating a partial template.

The failure UI identifies the validation problem and communicates that the import did not succeed.

The database is not modified when source validation fails.

The behavior is covered by tests and was manually verified through the application UI.

---

## 15. Security

The uploaded workbook is treated as untrusted input.

Important controls include:

- Validation before persistence
- HTML sanitization before rendering
- Restricted link protocols
- No direct rendering of raw comment HTML
- Database credentials supplied through environment variables
- `.env` excluded from version control

The HTML sanitizer is intentionally applied at the rendering boundary so that useful source formatting is not unnecessarily destroyed during migration.

---

## 16. Testing Strategy

The test suite covers several layers of the application.

### Mapping and Validation

Tests cover source validation, mapping behavior, schemas, and migration coverage.

### Import Services

Tests cover the import service and preview behavior.

### Persistence

Tests cover repository operations and database persistence.

### Duplication

Tests verify that duplicated templates are independent.

### HTML Security

Tests cover formatting, links, script content, and JavaScript URL cases.

### Real Fixture

The actual Spectora XLSX fixture is used to verify processing against realistic source data.

The final local test result is:

```text
23 passed
```

There is an upstream Starlette/AnyIO deprecation warning during the test run; it does not cause a test failure.

---

## 17. Design Decisions

### Why normalize the hierarchy?

The normalized model makes sections, items, and fields independently editable and persistent.

### Why separate validation from mapping?

Validation failures should be detected before transformation and database mutation.

### Why preview before persistence?

A migration preview provides visibility into the imported structure and coverage before the user commits it.

### Why preserve source metadata?

Source exports contain information that may not have a direct normalized representation. Preserving it reduces unnecessary information loss.

### Why sanitize HTML at render time?

Stripping HTML during import would destroy useful formatting. Rendering-time sanitization preserves source content while providing a security boundary.

### Why PostgreSQL?

The Template → Section → Item → Field structure is relational, making PostgreSQL a natural fit for the normalized model and persistent editing workflow.

---

## 18. Known Tradeoffs

### Preview Storage

Preview state is kept separately from persistent templates.

This is appropriate for the assignment workflow but is not intended as a distributed multi-instance import architecture.

A production implementation could introduce persistent import jobs with expiration, ownership, and resumability.

### Authentication

A full production authentication and authorization layer is outside the core assignment scope.

The application should therefore be treated as an assignment/demo implementation rather than a production SaaS security architecture.

### Source Format

The implementation focuses on the Spectora XLSX format used for the assignment.

Additional export variants may require additional mapping and validation rules.

### Photo Handling

The importer detects default photo columns and reports whether they contain populated values.

Photo/media storage and migration are not implemented as a separate media subsystem.

---

## 19. Potential Production Extensions

A production-oriented implementation could add:

1. Persistent import jobs
2. Background processing for large workbooks
3. Import history
4. Authentication and authorization
5. Template versioning
6. Rollback
7. More detailed source-to-target mapping reports
8. Dedicated photo/media migration
9. Progress reporting
10. Structured application logging
11. Observability and monitoring

---

## 20. Final Implementation Status

The following core workflow has been implemented:

```text
[X] XLSX upload
[X] Source validation
[X] Migration preview
[X] Structured hierarchy
[X] Database persistence
[X] Section editing
[X] Item editing
[X] Comment editing
[X] Independent duplication
[X] Rich HTML preservation
[X] HTML sanitization
[X] Source metadata preservation
[X] Failure handling
[X] Automated tests
```

Final local test status:

```text
23 passed
```

---

## Repository

GitHub repository:

https://github.com/PHENOGRAMMER/HIVE_TEMPLATE
