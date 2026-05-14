from app.db.repos.subscriptions import SubscriptionRepo
from app.db.repos.user_repo import UserRepository
from app.models.posts import TopicModel


async def test_subscription_create(db_session):
    """Test creating a subscription between a user and topic."""
    # Create a user
    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="test-user")
    user_id = user.id

    # Create a topic
    topic = TopicModel(name="test-topic")
    db_session.add(topic)
    await db_session.flush()
    await db_session.refresh(topic)
    topic_id = topic.id

    # Create a subscription
    subscription_repo = SubscriptionRepo(db_session)
    subscription = await subscription_repo.create(topic_id=topic_id, user_id=user_id)

    assert subscription.id is not None
    assert subscription.topic_id == topic_id
    assert subscription.user_id == user_id
    assert subscription.is_deleted is False


async def test_subscription_get_by_id(db_session):
    """Test retrieving a subscription by ID."""
    # Create a user and topic
    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="test-user")
    topic = TopicModel(name="test-topic")
    db_session.add(topic)
    await db_session.flush()
    await db_session.refresh(topic)

    # Create a subscription
    subscription_repo = SubscriptionRepo(db_session)
    created_subscription = await subscription_repo.create(
        topic_id=topic.id, user_id=user.id
    )
    subscription_id = created_subscription.id

    # Fetch the subscription by ID
    fetched_subscription = await subscription_repo.get_by_id(subscription_id)

    assert fetched_subscription is not None
    assert fetched_subscription.id == subscription_id
    assert fetched_subscription.topic_id == topic.id
    assert fetched_subscription.user_id == user.id
    assert fetched_subscription.is_deleted is False


async def test_subscription_get_by_id_not_found(db_session):
    """Test retrieving a non-existent subscription returns None."""
    subscription_repo = SubscriptionRepo(db_session)
    subscription = await subscription_repo.get_by_id("non-existent-id")
    assert subscription is None


async def test_subscription_delete(db_session):
    """Test soft deleting a subscription."""
    # Create a user and topic
    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="test-user")
    topic = TopicModel(name="test-topic")
    db_session.add(topic)
    await db_session.flush()
    await db_session.refresh(topic)

    # Create a subscription
    subscription_repo = SubscriptionRepo(db_session)
    subscription = await subscription_repo.create(topic_id=topic.id, user_id=user.id)

    # Delete the subscription
    deleted_subscription = await subscription_repo.delete(subscription)

    assert deleted_subscription is not None
    assert deleted_subscription.id == subscription.id
    assert deleted_subscription.is_deleted is True

    # Verify it's marked as deleted
    fetched = await subscription_repo.get_by_id(subscription.id)
    assert fetched is None


async def test_subscription_delete_include_deleted(db_session):
    """Test retrieving deleted subscription with include_deleted flag."""
    # Create a user and topic
    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="test-user")
    topic = TopicModel(name="test-topic")
    db_session.add(topic)
    await db_session.flush()
    await db_session.refresh(topic)

    # Create and delete a subscription
    subscription_repo = SubscriptionRepo(db_session)
    subscription = await subscription_repo.create(topic_id=topic.id, user_id=user.id)

    await subscription_repo.delete(subscription)

    # Verify deleted subscription is not found by default
    assert await subscription_repo.get_by_id(subscription.id) is None

    # Verify deleted subscription is found with include_deleted=True
    deleted_subscription = await subscription_repo.get_by_id(
        subscription.id, include_deleted=True
    )
    assert deleted_subscription is not None
    assert deleted_subscription.is_deleted is True


async def test_subscription_exists_true(db_session):
    """Test exists returns True for existing subscription."""
    # Create a user and topic
    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="test-user")
    topic = TopicModel(name="test-topic")
    db_session.add(topic)
    await db_session.flush()
    await db_session.refresh(topic)

    # Create a subscription
    subscription_repo = SubscriptionRepo(db_session)
    await subscription_repo.create(topic_id=topic.id, user_id=user.id)

    # Check if subscription exists
    exists = await subscription_repo.exists(user_id=user.id, topic_id=topic.id)
    assert exists is not None


async def test_subscription_exists_false(db_session):
    """Test exists returns False for non-existent subscription."""
    subscription_repo = SubscriptionRepo(db_session)
    exists = await subscription_repo.exists(
        user_id="non-existent-user", topic_id="non-existent-topic"
    )
    assert exists is None


async def test_subscription_exists_deleted(db_session):
    """Test exists with deleted subscriptions."""
    # Create a user and topic
    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="test-user")
    topic = TopicModel(name="test-topic")
    db_session.add(topic)
    await db_session.flush()
    await db_session.refresh(topic)

    # Create and delete a subscription
    subscription_repo = SubscriptionRepo(db_session)
    subscription = await subscription_repo.create(topic_id=topic.id, user_id=user.id)
    await subscription_repo.delete(subscription)

    # Verify deleted subscription doesn't exist by default
    exists = await subscription_repo.exists(user_id=user.id, topic_id=topic.id)
    assert exists is None

    # Verify deleted subscription exists with include_deleted=True
    exists_with_deleted = await subscription_repo.exists(
        user_id=user.id, topic_id=topic.id, include_deleted=True
    )
    assert exists_with_deleted is not None


async def test_subscription_multiple_users_same_topic(db_session):
    """Test multiple users can subscribe to the same topic."""
    # Create a topic
    topic = TopicModel(name="test-topic")
    db_session.add(topic)
    await db_session.flush()
    await db_session.refresh(topic)

    # Create multiple users
    user_repo = UserRepository(db_session)
    user1 = await user_repo.create(username="user1")
    user2 = await user_repo.create(username="user2")
    user3 = await user_repo.create(username="user3")

    # Subscribe all users to the topic
    subscription_repo = SubscriptionRepo(db_session)
    sub1 = await subscription_repo.create(topic_id=topic.id, user_id=user1.id)
    sub2 = await subscription_repo.create(topic_id=topic.id, user_id=user2.id)
    sub3 = await subscription_repo.create(topic_id=topic.id, user_id=user3.id)

    # Verify all subscriptions exist
    assert sub1.id is not None
    assert sub2.id is not None
    assert sub3.id is not None
    assert (
        await subscription_repo.exists(user_id=user1.id, topic_id=topic.id) is not None
    )
    assert (
        await subscription_repo.exists(user_id=user2.id, topic_id=topic.id) is not None
    )
    assert (
        await subscription_repo.exists(user_id=user3.id, topic_id=topic.id) is not None
    )


async def test_subscription_same_user_multiple_topics(db_session):
    """Test one user can subscribe to multiple topics."""
    # Create a user
    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="test-user")

    # Create multiple topics
    topic1 = TopicModel(name="topic-1")
    topic2 = TopicModel(name="topic-2")
    topic3 = TopicModel(name="topic-3")
    db_session.add_all([topic1, topic2, topic3])
    await db_session.flush()
    await db_session.refresh(topic1)
    await db_session.refresh(topic2)
    await db_session.refresh(topic3)

    # Subscribe user to all topics
    subscription_repo = SubscriptionRepo(db_session)
    sub1 = await subscription_repo.create(topic_id=topic1.id, user_id=user.id)
    sub2 = await subscription_repo.create(topic_id=topic2.id, user_id=user.id)
    sub3 = await subscription_repo.create(topic_id=topic3.id, user_id=user.id)

    # Verify all subscriptions exist
    assert sub1.id is not None
    assert sub2.id is not None
    assert sub3.id is not None
    assert (
        await subscription_repo.exists(user_id=user.id, topic_id=topic1.id) is not None
    )
    assert (
        await subscription_repo.exists(user_id=user.id, topic_id=topic2.id) is not None
    )
    assert (
        await subscription_repo.exists(user_id=user.id, topic_id=topic3.id) is not None
    )
