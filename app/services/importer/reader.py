from pathlib import Path
from zipfile import is_zipfile

import pandas as pd


SUPPORTED_EXTENSIONS = {".xls", ".xlsx"}


def read_template_file(file_path: str | Path) -> pd.DataFrame:
    """
    Read a Spectora Excel template export.

    Supports both .xls and .xlsx.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}. "
            f"Expected: .xls or .xlsx"
        )

    if extension == ".xls" and not is_zipfile(path):
        return pd.read_excel(path, engine="xlrd")

    return pd.read_excel(path, engine="openpyxl")