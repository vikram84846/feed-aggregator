"""
topic subscription for database operations related to user subscrption to topic .

Responsibilities:
    - create user subscription for topic
    - fetch subscription(s) by id/user/topic
    - soft delete user subscription for topic

NOTE:
    - Repository layer should remain dumb.
    - No commits inside repository.
    - Transaction lifecycle handled by service layer.
"""

from app.db.repos.base_repo import BaseRepository
from app.models.users import TopicSubscriptionModel
from sqlalchemy import select


class SubscriptionRepo(BaseRepository):
    async def create(self, topic_id: str, user_id: str) -> TopicSubscriptionModel:
        """
        subscribes user to the topic
        Args:
            - topic_id : unique identifier for topic
            - user_id : unique identifier for user
        """
        subscription = TopicSubscriptionModel(topic_id=topic_id, user_id=user_id)
        self._session.add(subscription)
        await self._session.flush()
        await self._session.refresh(subscription)
        return subscription

    async def get_by_id(
        self, subscription_id: str, include_deleted: bool = False
    ) -> TopicSubscriptionModel | None:
        """
        returns the subscription details using unique subcription identifier
        Args:
            - subscription_id : unique identifier for subscription identification
            - include_deleted : includes soft deleted subscriptions
        """
        stmt = select(TopicSubscriptionModel).where(
            TopicSubscriptionModel.id == subscription_id
        )

        if not include_deleted:
            stmt = stmt.where(TopicSubscriptionModel.is_deleted.is_(False))
        subscription = await self._session.execute(stmt)
        return subscription.scalar_one_or_none()

    async def delete(
        self, subscription: TopicSubscriptionModel
    ) -> TopicSubscriptionModel | None:
        """
        soft deletes user subscription for the topic
        Args:
            - subscription : subscription object to be deleted
        """
        subscription.is_deleted = True
        await self._session.flush()
        return subscription

    async def exists(
        self, user_id: str, topic_id: str, include_deleted: bool = False
    ) -> TopicSubscriptionModel:
        """
        returns True if subscription exists else False
        Agrs:
            user_id : unique identification for user
            topic_id : unique identification for topic
        """
        stmt = select(TopicSubscriptionModel).where(
            TopicSubscriptionModel.user_id == user_id,
            TopicSubscriptionModel.topic_id == topic_id,
        )

        if not include_deleted:
            stmt = stmt.where(TopicSubscriptionModel.is_deleted.is_(False))
        subscription = await self._session.execute(stmt)
        return subscription.scalar_one_or_none()
