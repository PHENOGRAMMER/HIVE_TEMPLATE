from app.database.connection import Base, engine

# Import the models so SQLAlchemy registers every table.
from app.database.models import Item, Section, Template, TemplateField  # noqa: F401


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    main()