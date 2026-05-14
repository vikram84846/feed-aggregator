from app.db.repos.subscriptions import SubscriptionRepo
from app.db.repos.post_repo import TopicRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repos.user_repo import UserRepository
from fastapi import HTTPException, status


class SubscriptionService:
    def __init__(self, session: AsyncSession):
        self.subscription_repo = SubscriptionRepo(session)
        self.user_repo = UserRepository(session)
        self.topic_repo = TopicRepository(session)

    async def subscribe(self, user_id: str, topic_name: str):
        """subscribes user to the topic"""
        # check if topic exists
        topic = await self.topic_repo.get_by_name(topic_name)
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="topic not found"
            )
        # check if subscription already exists
        subscription = await self.subscription_repo.exists(
            user_id, topic.id, include_deleted=True
        )
        if subscription:
            # is soft deleted set is_deleted false
            if subscription.is_deleted:
                subscription.is_deleted = False
                return subscription
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="subscription already exists",
            )
        subscription = await self.subscription_repo.create(topic.id, user_id)
        return subscription

    async def unsubscribe(self, topic_name: str, user_id: str):
        """soft deletes user subscription for topic"""
        # check if topic exists
        topic = await self.topic_repo.get_by_name(topic_name)
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="topic not found"
            )
        # check if subscription exists
        subscription = await self.subscription_repo.exists(user_id, topic.id)
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="subscription not found"
            )
        return await self.subscription_repo.delete(subscription)

    async def get_user_subscribed_topics(self, user_id: str):
        """
        retruns the list of topics subscribed by user
        """
        topics = await self.user_repo.get_subscribed_topics(user_id)
        return topics

    async def get_topic_subscribed_users(self, topic_name: str):
        topic = await self.topic_repo.get_by_name(topic_name)
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="topic not found"
            )
        users = await self.topic_repo.get_subscribed_users(topic.id)
        return users
