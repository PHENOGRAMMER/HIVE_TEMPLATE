from sqlalchemy import text

from app.database.connection import engine


def main() -> None:
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print(
                "Database connection successful:",
                result.scalar(),
            )
    except Exception as exc:
        print("Database connection failed.")
        print(f"{type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()