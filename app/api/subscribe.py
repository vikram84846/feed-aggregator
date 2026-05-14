from fastapi import APIRouter, Depends, status
from app.services.subscription import SubscriptionService
from app.utils.dependency import get_current_user
from app.models.users import UserModel
from app.schema.subscription_schema import (
    SubscriptionSchema,
    SubscriptionResponseSchema,
    UserTopicsResponse,
)
from app.db.db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/subscriptions", tags=["Topic Subscriptions"])


@router.post(
    "/subscribe",
    response_model=SubscriptionResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def subscribe_topic(
    payload: SubscriptionSchema,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    subscribes user to the topic
    """
    subscription_service = SubscriptionService(session)
    subscription = await subscription_service.subscribe(
        current_user.id, payload.topic_name
    )
    return subscription


@router.delete("/unsubscribe/{topic_name}", status_code=status.HTTP_204_NO_CONTENT)
async def unsubscribe_topic(
    topic_name: str,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    unsubscribe user from topic
    """
    subscription_service = SubscriptionService(session)
    await subscription_service.unsubscribe(topic_name, current_user.id)


@router.get("/", status_code=status.HTTP_200_OK, response_model=UserTopicsResponse)
async def get_user_subscribed_topic(
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    return the list of topics user subscribed to
    """
    subscription_service = SubscriptionService(session)
    topics = await subscription_service.get_user_subscribed_topics(current_user.id)
    return UserTopicsResponse(topics=topics)
