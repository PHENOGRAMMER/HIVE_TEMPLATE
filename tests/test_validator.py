import pandas as pd

from app.services.importer.validator import validate_dataframe


def test_valid_spectora_dataframe_has_no_errors():
    df = pd.DataFrame(
        {
            "Section Name": ["Exterior"],
            "Item Name": ["Siding"],
            "Comment Name": ["Cracking - Major"],
            "Comment Text": ["Cracking observed."],
            "Comment Type (info, limit, defect)": ["defect"],
            "Category (-1: Low, 0: Med, 1: High)": [0],
            "Multiple Choice Options (comma-separated)": [None],
            "Unit Type Options (numeric answers only, comma-separated)": [
                None
            ],
            "Recommendation (from list)": [None],
            "Order (w/i item)": [0],
            "Answer Type (boolean, checkbox, date, number, range, text)": [
                "boolean"
            ],
            "Default Value": [None],
            "Default Value 2 (for \"range\" types)": [None],
            "Default Unit Type (for \"number\" and \"range\" types)": [
                None
            ],
            "Default Location": [None],
            "Default Estimate Min": [10],
            "Default Estimate Max": [1000],
            "Locked": [None],
            "Simple Format": [None],
            "Disable Photos": [None],
            "Uses": [0],
            "Last Modified": ["09/20/2026"],
        }
    )

    issues = validate_dataframe(df)

    assert issues == []