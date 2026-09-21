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