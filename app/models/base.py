"""
Base SQLAlchemy models and mixins for common fields.
"""

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid import uuid4
from sqlalchemy import DateTime
from datetime import datetime, timezone


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class TimeStampMixin:
    """Mixin to add created_at and updated_at timestamp fields."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class UUIDMixin:
    """Mixin to add a UUID primary key field."""

    id: Mapped[str] = mapped_column(default=lambda: str(uuid4()), primary_key=True)


class SoftDeletedMixin:
    """Mixin to add a soft delete flag."""

    is_deleted: Mapped[bool] = mapped_column(default=False)
