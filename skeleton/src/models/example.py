{%- if values.orm == "sqlalchemy" and values.database != "dynamodb" and values.database != "none" %}
"""Example model."""

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin, UUIDMixin


class Example(Base, UUIDMixin, TimestampMixin):
    """Example database model."""

    __tablename__ = "examples"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Example(id={self.id}, name={self.name})>"
{%- elif values.orm == "sqlmodel" and values.database != "dynamodb" and values.database != "none" %}
"""Example model using SQLModel."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Example(SQLModel, table=True):
    """Example database model."""

    __tablename__ = "examples"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255, index=True)
    description: str | None = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
{%- else %}
# Database/ORM not enabled
{%- endif %}
