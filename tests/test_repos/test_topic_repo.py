from app.db.repos.post_repo import TopicRepository
from app.db.repos.subscriptions import SubscriptionRepo
from app.db.repos.user_repo import UserRepository


async def test_topic_create(db_session):
    topic_repo = TopicRepository(db_session)
    topic = await topic_repo.create("test-topic")
    assert topic.id is not None
    assert topic.name == "test-topic"
    assert topic.is_deleted is False


async def test_get_by_id(db_session):
    topic_repo = TopicRepository(db_session)
    topic = await topic_repo.create("topic-by-id")
    topic_id = topic.id
    fetched = await topic_repo.get_by_id(topic_id)
    assert fetched is not None
    assert fetched.id == topic_id
    assert fetched.name == "topic-by-id"


async def test_get_by_name(db_session):
    topic_repo = TopicRepository(db_session)
    await topic_repo.create("topic-by-name")
    fetched = await topic_repo.get_by_name("topic-by-name")
    assert fetched is not None
    assert fetched.name == "topic-by-name"


async def test_topic_delete(db_session):
    topic_repo = TopicRepository(db_session)
    topic = await topic_repo.create("topic-to-delete")
    topic_id = topic.id
    deleted = await topic_repo.delete(topic_id)
    assert deleted.is_deleted is True
    # Should not return in normal get
    assert await topic_repo.get_by_id(topic_id) is None
    # Should return if include_deleted=True
    assert await topic_repo.get_by_id(topic_id, include_deleted=True) is not None


async def test_get_by_id_not_found(db_session):
    topic_repo = TopicRepository(db_session)
    assert await topic_repo.get_by_id("non-existent-id") is None


async def test_get_by_name_not_found(db_session):
    topic_repo = TopicRepository(db_session)
    assert await topic_repo.get_by_name("non-existent-name") is None


async def test_get_subscribed_users_no_subscriptions(db_session):
    """Test get_subscribed_users returns empty list for topic with no subscriptions."""
    topic_repo = TopicRepository(db_session)
    topic = await topic_repo.create("tech-news")

    users = await topic_repo.get_subscribed_users(topic.id)

    assert users == []


async def test_get_subscribed_users_single_subscription(db_session):
    """Test get_subscribed_users returns single user subscription."""
    topic_repo = TopicRepository(db_session)
    topic = await topic_repo.create("tech-news")

    # Create a user
    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="alice")

    # Subscribe user to topic
    subscription_repo = SubscriptionRepo(db_session)
    await subscription_repo.create(topic_id=topic.id, user_id=user.id)

    # Refresh topic to load relationships
    await db_session.refresh(topic)

    users = await topic_repo.get_subscribed_users(topic.id)

    assert users is not None
    assert len(users) == 1
    assert "alice" in users


async def test_get_subscribed_users_multiple_subscriptions(db_session):
    """Test get_subscribed_users returns multiple user subscriptions."""
    topic_repo = TopicRepository(db_session)
    topic = await topic_repo.create("tech-news")

    # Create multiple users
    user_repo = UserRepository(db_session)
    user1 = await user_repo.create(username="alice")
    user2 = await user_repo.create(username="bob")
    user3 = await user_repo.create(username="charlie")

    # Subscribe all users to topic
    subscription_repo = SubscriptionRepo(db_session)
    await subscription_repo.create(topic_id=topic.id, user_id=user1.id)
    await subscription_repo.create(topic_id=topic.id, user_id=user2.id)
    await subscription_repo.create(topic_id=topic.id, user_id=user3.id)

    # Refresh topic to load relationships
    await db_session.refresh(topic)

    users = await topic_repo.get_subscribed_users(topic.id)

    assert users is not None
    assert len(users) == 3
    assert "alice" in users
    assert "bob" in users
    assert "charlie" in users


async def test_get_subscribed_users_topic_not_found(db_session):
    """Test get_subscribed_users returns None for non-existent topic."""
    topic_repo = TopicRepository(db_session)

    users = await topic_repo.get_subscribed_users("non-existent-topic")

    assert users is None
