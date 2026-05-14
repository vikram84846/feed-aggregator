"""
Model for content sources (e.g., RSS feeds).
"""

from app.models.base import Base, TimeStampMixin, UUIDMixin, SoftDeletedMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.posts import PostModel


class SourceModel(Base, TimeStampMixin, UUIDMixin, SoftDeletedMixin):
    """Model for a content source (e.g., website, feed)."""

    __tablename__ = "sources"

    name: Mapped[str] = mapped_column(unique=True, index=True)
    base_url: Mapped[str] = mapped_column(unique=True, index=True)

    posts: Mapped[list["PostModel"]] = relationship(
        "PostModel", back_populates="source", lazy="selectin"
    )
