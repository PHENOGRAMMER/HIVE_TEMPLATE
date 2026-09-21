from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class Template(Base):
    __tablename__ = "templates"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    source_file: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    sections: Mapped[list["Section"]] = relationship(
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="Section.position",
    )


class Section(Base):
    __tablename__ = "sections"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    template_id: Mapped[UUID] = mapped_column(
        ForeignKey("templates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    template: Mapped["Template"] = relationship(
        back_populates="sections",
    )

    items: Mapped[list["Item"]] = relationship(
        back_populates="section",
        cascade="all, delete-orphan",
        order_by="Item.position",
    )


class Item(Base):
    __tablename__ = "items"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    section_id: Mapped[UUID] = mapped_column(
        ForeignKey("sections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    section: Mapped["Section"] = relationship(
        back_populates="items",
    )

    fields: Mapped[list["TemplateField"]] = relationship(
        back_populates="item",
        cascade="all, delete-orphan",
        order_by="TemplateField.position",
    )


class TemplateField(Base):
    __tablename__ = "fields"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    item_id: Mapped[UUID] = mapped_column(
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    comment_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    comment_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    category: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    answer_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    options: Mapped[list[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )

    unit_options: Mapped[list[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )

    recommendation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    source_order: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    default_value: Mapped[Any | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    default_value_2: Mapped[Any | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    default_unit_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    default_location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    estimate_min: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    estimate_max: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    locked: Mapped[bool | None] = mapped_column(
        nullable=True,
    )

    simple_format: Mapped[bool | None] = mapped_column(
        nullable=True,
    )

    disable_photos: Mapped[bool | None] = mapped_column(
        nullable=True,
    )

    uses: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    source_row: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    source_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    item: Mapped["Item"] = relationship(
        back_populates="fields",
    )