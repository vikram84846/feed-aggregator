from app.db.repos.user_repo import UserRepository
from app.db.repos.subscriptions import SubscriptionRepo
from app.models.posts import TopicModel


async def test_user_create_username_only(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="karan")
    assert user.id is not None
    assert user.username == "karan"
    assert user.email is None
    assert user.password_hash is None
    assert user.is_deleted is False


async def test_user_create_with_password_hash(db_session):
    user_repo = UserRepository(db_session)

    user = await user_repo.create(
        username="test-user", password_hash="test_hash_password"
    )
    assert user.id is not None
    assert user.username == "test-user"
    assert user.email is None
    assert user.password_hash == "test_hash_password"
    assert user.is_deleted is False


async def test_user_create_with_email_and_password_hash(db_session):
    user_repo = UserRepository(db_session)

    user = await user_repo.create(
        username="test-user",
        password_hash="test_hash_password",
        email="Test123@test.com",
    )
    assert user.id is not None
    assert user.username == "test-user"
    assert user.email == "Test123@test.com"
    assert user.password_hash == "test_hash_password"
    assert user.is_deleted is False


async def test_user_get_by_id(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create(
        username="test-user",
        password_hash="test_hash_password",
        email="Test123@test.com",
    )
    user_id = user.id

    # fetch the user by id
    test_user = await user_repo.get_by_id(user_id)
    assert test_user.id == user_id
    assert test_user.username == "test-user"
    assert test_user.password_hash == "test_hash_password"
    assert test_user.email == "Test123@test.com"


async def test_user_get_by_email(db_session):
    user_repo = UserRepository(db_session)
    await user_repo.create(
        username="test-user",
        password_hash="test_hash_password",
        email="Test123@test.com",
    )

    # fetch the user by email
    test_user = await user_repo.get_by_email("Test123@test.com")
    assert test_user.id is not None
    assert test_user.username == "test-user"
    assert test_user.password_hash == "test_hash_password"
    assert test_user.email == "Test123@test.com"


async def test_user_get_by_username(db_session):
    user_repo = UserRepository(db_session)
    await user_repo.create(
        username="test-user",
        password_hash="test_hash_password",
        email="Test123@test.com",
    )

    # fetch the user by username
    test_user = await user_repo.get_by_username("test-user")
    assert test_user.id is not None
    assert test_user.username == "test-user"
    assert test_user.password_hash == "test_hash_password"
    assert test_user.email == "Test123@test.com"


async def test_user_delete(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create(
        username="test-user",
        password_hash="test_hash_password",
        email="Test123@test.com",
    )
    user_id = user.id

    # delete the user by id
    test_user = await user_repo.delete(user_id)
    assert test_user.is_deleted is True


async def test_get_by_invalid_id(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.get_by_id("invalid-id")
    assert user is None


async def test_get_by_invalid_username(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.get_by_username("invalid-username")
    assert user is None


async def test_get_by_invalid_email(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.get_by_email("invalid-email")
    assert user is None


async def test_delete_invalid_user(db_session):
    user_repo = UserRepository(db_session)

    # delete the user by id
    test_user = await user_repo.delete("invalid-id")
    assert test_user is None


async def test_user_delete_deleted_user(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create(
        username="test-user",
        password_hash="test_hash_password",
        email="Test123@test.com",
    )
    user_id = user.id

    # delete the user by id
    await user_repo.delete(user_id)
    test_user = await user_repo.delete(user_id)
    assert test_user.is_deleted is True


async def test_get_subscribed_topics_no_subscriptions(db_session):
    """Test get_subscribed_topics returns empty list for user with no subscriptions."""
    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="test-user")

    topics = await user_repo.get_subscribed_topics(user.id)

    assert topics == []


async def test_get_subscribed_topics_single_subscription(db_session):
    """Test get_subscribed_topics returns single topic subscription."""
    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="test-user")

    # Create a topic
    topic = TopicModel(name="python-tips")
    db_session.add(topic)
    await db_session.flush()
    await db_session.refresh(topic)

    # Subscribe user to topic
    subscription_repo = SubscriptionRepo(db_session)
    await subscription_repo.create(topic_id=topic.id, user_id=user.id)

    # Refresh user to load relationships
    await db_session.refresh(user)

    topics = await user_repo.get_subscribed_topics(user.id)

    assert topics is not None
    assert len(topics) == 1
    assert "python-tips" in topics


async def test_get_subscribed_topics_multiple_subscriptions(db_session):
    """Test get_subscribed_topics returns multiple topic subscriptions."""
    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="test-user")

    # Create multiple topics
    topic1 = TopicModel(name="python")
    topic2 = TopicModel(name="javascript")
    topic3 = TopicModel(name="rust")
    db_session.add_all([topic1, topic2, topic3])
    await db_session.flush()
    await db_session.refresh(topic1)
    await db_session.refresh(topic2)
    await db_session.refresh(topic3)

    # Subscribe user to all topics
    subscription_repo = SubscriptionRepo(db_session)
    await subscription_repo.create(topic_id=topic1.id, user_id=user.id)
    await subscription_repo.create(topic_id=topic2.id, user_id=user.id)
    await subscription_repo.create(topic_id=topic3.id, user_id=user.id)

    # Refresh user to load relationships
    await db_session.refresh(user)

    topics = await user_repo.get_subscribed_topics(user.id)

    assert topics is not None
    assert len(topics) == 3
    assert "python" in topics
    assert "javascript" in topics
    assert "rust" in topics


async def test_get_subscribed_topics_user_not_found(db_session):
    """Test get_subscribed_topics returns None for non-existent user."""
    user_repo = UserRepository(db_session)

    topics = await user_repo.get_subscribed_topics("non-existent-user")

    assert topics is None
