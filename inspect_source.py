from app.services.importer.reader import read_template_file


FILE_PATH = "data/fixtures/InterNACHI Residential -2026-09-20.xlsx"

ANSWER_TYPE_COLUMN = (
    "Answer Type (boolean, checkbox, date, number, range, text)"
)

COMMENT_TYPE_COLUMN = (
    "Comment Type (info, limit, defect)"
)


def main() -> None:
    df = read_template_file(FILE_PATH)

    print("\n=== WORKBOOK OVERVIEW ===")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\n=== COLUMNS ===")
    for index, column in enumerate(df.columns, start=1):
        print(f"{index:02d}. {column}")

    print("\n=== FIRST 10 ROWS ===")
    print(df.head(10).to_string())

    print("\n=== ANSWER TYPES ===")
    if ANSWER_TYPE_COLUMN in df.columns:
        print(
            df[ANSWER_TYPE_COLUMN]
            .fillna("<empty>")
            .value_counts()
        )
    else:
        print(f"Column not found: {ANSWER_TYPE_COLUMN}")

    print("\n=== COMMENT TYPES ===")
    if COMMENT_TYPE_COLUMN in df.columns:
        print(
            df[COMMENT_TYPE_COLUMN]
            .fillna("<empty>")
            .value_counts()
        )
    else:
        print(f"Column not found: {COMMENT_TYPE_COLUMN}")


if __name__ == "__main__":
    main()