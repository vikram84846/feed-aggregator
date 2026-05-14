"""
Models for posts, topics, and their relationships.
"""

from app.models.base import Base, TimeStampMixin, UUIDMixin, SoftDeletedMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, ForeignKey, DateTime, UniqueConstraint
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.users import UserModel  # used to avoid circular imports
    from app.models.sources import SourceModel


class PostTopicModel(Base, TimeStampMixin, UUIDMixin, SoftDeletedMixin):
    __tablename__ = "post_topics"

    """Association table for posts and topics."""
    topic_id: Mapped[str] = mapped_column(ForeignKey("topics.id"))
    post_id: Mapped[str] = mapped_column(ForeignKey("posts.id"))

    __table_args__ = (UniqueConstraint("topic_id", "post_id", name="uq_post_topic"),)


class TopicModel(Base, TimeStampMixin, UUIDMixin, SoftDeletedMixin):
    __tablename__ = "topics"

    """Model for topics that group posts and users."""
    name: Mapped[str] = mapped_column(index=True, unique=True)

    users: Mapped[list["UserModel"]] = relationship(
        "UserModel",
        secondary="topic_subscriptions",
        back_populates="topics",
        lazy="selectin",
    )
    posts: Mapped[list["PostModel"]] = relationship(
        "PostModel", secondary="post_topics", back_populates="topics", lazy="selectin"
    )


class PostModel(Base, UUIDMixin, SoftDeletedMixin, TimeStampMixin):
    __tablename__ = "posts"

    """Model for posts/articles from sources."""
    title: Mapped[str] = mapped_column(index=True)
    content: Mapped[str] = mapped_column(Text)
    url: Mapped[str] = mapped_column(unique=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"))
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    topics: Mapped[list["TopicModel"]] = relationship(
        "TopicModel", secondary="post_topics", back_populates="posts", lazy="selectin"
    )
    source: Mapped["SourceModel"] = relationship("SourceModel", back_populates="posts")
