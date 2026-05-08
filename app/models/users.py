"""
Models for users and topic subscriptions.
"""
from app.models.base import Base, TimeStampMixin, UUIDMixin, SoftDeletedMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.posts import TopicModel  #used to avoid circular imports


class TopicSubscriptionModel(Base,TimeStampMixin,UUIDMixin,SoftDeletedMixin):
    """Association table for user subscriptions to topics."""
    __tablename__ = "topic_subscriptions"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    topic_id: Mapped[str] = mapped_column(ForeignKey('topics.id'))

    __table_args__ = (
        UniqueConstraint("user_id","topic_id",name="uq_user_topic"),
    )

class UserModel(Base,TimeStampMixin,UUIDMixin,SoftDeletedMixin):
    """Model for application users."""
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(unique=True,index=True)
    password_hash: Mapped[str] = mapped_column(nullable=True) #to support oauth later
    email: Mapped[str] = mapped_column(unique=True,nullable=True) #later to support via phone also (2 seprate fields required phone and email and username to uniqly identify the user)

    topics: Mapped[list["TopicModel"]] = relationship("TopicModel",secondary="topic_subscriptions",back_populates="users")


#users subscribe to topic 
