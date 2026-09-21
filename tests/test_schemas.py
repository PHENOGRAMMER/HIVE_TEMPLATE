from app.schemas.template import ImportedField


def test_imported_field_accepts_valid_data():
    field = ImportedField(
        name="Cracking - Major",
        comment_text=(
            "Moderate to major cracking was observed."
        ),
        comment_type="defect",
        category=0,
        answer_type="boolean",
        order=2,
        source_row=9,
    )

    assert field.name == "Cracking - Major"
    assert field.comment_type == "defect"
    assert field.answer_type == "boolean"
    assert field.category == 0
    assert field.source_row == 9