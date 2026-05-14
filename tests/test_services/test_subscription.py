from fastapi import HTTPException

from app.services.subscription import SubscriptionService

from app.models.users import UserModel, TopicSubscriptionModel
from app.models.posts import TopicModel


async def test_subscribe_success(
    db_session,
):
    subscription_service = SubscriptionService(db_session)

    user = UserModel(
        username="testuser",
        email="test@example.com",
        password_hash="hashedpassword",
    )

    topic = TopicModel(
        name="python",
    )

    db_session.add(user)
    db_session.add(topic)

    await db_session.flush()

    subscription = await subscription_service.subscribe(
        user.id,
        topic.name,
    )

    assert subscription is not None
    assert subscription.user_id == user.id
    assert subscription.topic_id == topic.id
    assert subscription.is_deleted is False


async def test_subscribe_topic_not_found(
    db_session,
):
    subscription_service = SubscriptionService(db_session)

    user = UserModel(
        username="testuser",
        email="test@example.com",
        password_hash="hashedpassword",
    )

    db_session.add(user)

    await db_session.flush()

    try:
        await subscription_service.subscribe(
            user.id,
            "invalid-topic",
        )

        assert False

    except HTTPException as exc:
        assert exc.status_code == 404
        assert exc.detail == "topic not found"


async def test_subscribe_restores_soft_deleted_subscription(
    db_session,
):
    subscription_service = SubscriptionService(db_session)

    user = UserModel(
        username="testuser",
        email="test@example.com",
        password_hash="hashedpassword",
    )

    topic = TopicModel(
        name="python",
    )

    db_session.add(user)
    db_session.add(topic)

    await db_session.flush()

    subscription = TopicSubscriptionModel(
        user_id=user.id,
        topic_id=topic.id,
        is_deleted=True,
    )

    db_session.add(subscription)

    await db_session.flush()

    restored_subscription = await subscription_service.subscribe(
        user.id,
        topic.name,
    )

    assert restored_subscription.id == subscription.id
    assert restored_subscription.is_deleted is False


async def test_unsubscribe_success(
    db_session,
):
    subscription_service = SubscriptionService(db_session)

    user = UserModel(
        username="testuser",
        email="test@example.com",
        password_hash="hashedpassword",
    )

    topic = TopicModel(
        name="python",
    )

    db_session.add(user)
    db_session.add(topic)

    await db_session.flush()

    subscription = TopicSubscriptionModel(
        user_id=user.id,
        topic_id=topic.id,
    )

    db_session.add(subscription)

    await db_session.flush()

    await subscription_service.unsubscribe(
        topic.name,
        user.id,
    )

    assert subscription.is_deleted is True


async def test_unsubscribe_topic_not_found(
    db_session,
):
    subscription_service = SubscriptionService(db_session)

    user = UserModel(
        username="testuser",
        email="test@example.com",
        password_hash="hashedpassword",
    )

    db_session.add(user)

    await db_session.flush()

    try:
        await subscription_service.unsubscribe(
            "invalid-topic",
            user.id,
        )

        assert False

    except HTTPException as exc:
        assert exc.status_code == 404
        assert exc.detail == "topic not found"


async def test_unsubscribe_subscription_not_found(
    db_session,
):
    subscription_service = SubscriptionService(db_session)

    user = UserModel(
        username="testuser",
        email="test@example.com",
        password_hash="hashedpassword",
    )

    topic = TopicModel(
        name="python",
    )

    db_session.add(user)
    db_session.add(topic)

    await db_session.flush()

    try:
        await subscription_service.unsubscribe(
            topic.name,
            user.id,
        )

        assert False

    except HTTPException as exc:
        assert exc.status_code == 404
        assert exc.detail == "subscription not found"


async def test_get_user_subscribed_topics(
    db_session,
):
    subscription_service = SubscriptionService(db_session)

    user = UserModel(
        username="testuser",
        email="test@example.com",
        password_hash="hashedpassword",
    )

    topic1 = TopicModel(name="python")
    topic2 = TopicModel(name="fastapi")

    db_session.add(user)
    db_session.add(topic1)
    db_session.add(topic2)

    await db_session.flush()

    subscription1 = TopicSubscriptionModel(
        user_id=user.id,
        topic_id=topic1.id,
    )

    subscription2 = TopicSubscriptionModel(
        user_id=user.id,
        topic_id=topic2.id,
    )

    db_session.add(subscription1)
    db_session.add(subscription2)

    await db_session.flush()

    topics = await subscription_service.get_user_subscribed_topics(
        user.id,
    )

    assert len(topics) == 2

    assert "python" in topics
    assert "fastapi" in topics


async def test_get_user_subscribed_topics_empty(
    db_session,
):
    subscription_service = SubscriptionService(db_session)

    user = UserModel(
        username="testuser",
        email="test@example.com",
        password_hash="hashedpassword",
    )

    db_session.add(user)

    await db_session.flush()

    topics = await subscription_service.get_user_subscribed_topics(
        user.id,
    )

    assert topics == []


async def test_get_topic_subscribed_users(
    db_session,
):
    subscription_service = SubscriptionService(db_session)

    user1 = UserModel(
        username="user1",
        email="user1@example.com",
        password_hash="hashedpassword",
    )

    user2 = UserModel(
        username="user2",
        email="user2@example.com",
        password_hash="hashedpassword",
    )

    topic = TopicModel(
        name="python",
    )

    db_session.add(user1)
    db_session.add(user2)
    db_session.add(topic)

    await db_session.flush()

    subscription1 = TopicSubscriptionModel(
        user_id=user1.id,
        topic_id=topic.id,
    )

    subscription2 = TopicSubscriptionModel(
        user_id=user2.id,
        topic_id=topic.id,
    )

    db_session.add(subscription1)
    db_session.add(subscription2)

    await db_session.flush()

    users = await subscription_service.get_topic_subscribed_users(
        topic.name,
    )

    assert len(users) == 2

    assert "user1" in users
    assert "user2" in users


async def test_get_topic_subscribed_users_empty(
    db_session,
):
    subscription_service = SubscriptionService(db_session)

    topic = TopicModel(
        name="python",
    )

    db_session.add(topic)

    await db_session.flush()

    users = await subscription_service.get_topic_subscribed_users(
        topic.name,
    )

    assert users == []


async def test_get_topic_subscribed_users_topic_not_found(
    db_session,
):
    subscription_service = SubscriptionService(db_session)

    try:
        await subscription_service.get_topic_subscribed_users(
            "invalid-topic",
        )

        assert False

    except HTTPException as exc:
        assert exc.status_code == 404
        assert exc.detail == "topic not found"
