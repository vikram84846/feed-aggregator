from app.db.repos.feed_repo import FeedRepo
from app.db.repos.subscriptions import SubscriptionRepo
from app.db.repos.user_repo import UserRepository
from app.models.posts import PostModel, TopicModel
from app.models.sources import SourceModel


async def test_user_feed_returns_subscribed_posts(db_session):
    """Test feed returns posts from subscribed topics."""

    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="test-user")

    topic = TopicModel(name="technology")
    db_session.add(topic)

    source = SourceModel(
        name="BBC",
        base_url="https://bbc.com",
    )
    db_session.add(source)

    await db_session.flush()

    subscription_repo = SubscriptionRepo(db_session)

    await subscription_repo.create(
        user_id=user.id,
        topic_id=topic.id,
    )

    post = PostModel(
        title="Tech News",
        content="Latest technology updates",
        url="https://bbc.com/tech-news",
        source_id=source.id,
        topics=[topic],
    )

    db_session.add(post)

    await db_session.commit()

    post_id = post.id

    feed_repo = FeedRepo(db_session)

    total, feed = await feed_repo.user_feed(
        user_id=user.id,
        offset=0,
        limit=10,
    )

    assert total == 1
    assert len(feed) == 1
    assert feed[0].id == post_id
    assert feed[0].title == "Tech News"


async def test_user_feed_excludes_unsubscribed_posts(db_session):
    """Test feed excludes unsubscribed topic posts."""

    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="test-user")

    subscribed_topic = TopicModel(name="technology")
    unsubscribed_topic = TopicModel(name="sports")

    source = SourceModel(
        name="ESPN",
        base_url="https://espn.com",
    )

    db_session.add_all(
        [
            subscribed_topic,
            unsubscribed_topic,
            source,
        ]
    )

    await db_session.flush()

    subscription_repo = SubscriptionRepo(db_session)

    await subscription_repo.create(
        user_id=user.id,
        topic_id=subscribed_topic.id,
    )

    post = PostModel(
        title="Football News",
        content="Sports updates",
        url="https://espn.com/football",
        source_id=source.id,
        topics=[unsubscribed_topic],
    )

    db_session.add(post)

    await db_session.commit()

    feed_repo = FeedRepo(db_session)

    total, feed = await feed_repo.user_feed(
        user_id=user.id,
        offset=0,
        limit=10,
    )

    assert total == 0
    assert len(feed) == 0


async def test_user_feed_filter_by_topic_name(db_session):
    """Test filtering feed by topic name."""

    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="test-user")

    tech_topic = TopicModel(name="technology")
    sports_topic = TopicModel(name="sports")

    source = SourceModel(
        name="CNN",
        base_url="https://cnn.com",
    )

    db_session.add_all(
        [
            tech_topic,
            sports_topic,
            source,
        ]
    )

    await db_session.flush()

    subscription_repo = SubscriptionRepo(db_session)

    await subscription_repo.create(
        user_id=user.id,
        topic_id=tech_topic.id,
    )

    await subscription_repo.create(
        user_id=user.id,
        topic_id=sports_topic.id,
    )

    tech_post = PostModel(
        title="AI News",
        content="AI updates",
        url="https://cnn.com/ai",
        source_id=source.id,
        topics=[tech_topic],
    )

    sports_post = PostModel(
        title="Sports News",
        content="Football updates",
        url="https://cnn.com/sports",
        source_id=source.id,
        topics=[sports_topic],
    )

    db_session.add_all(
        [
            tech_post,
            sports_post,
        ]
    )

    await db_session.commit()

    feed_repo = FeedRepo(db_session)

    total, feed = await feed_repo.user_feed(
        user_id=user.id,
        offset=0,
        limit=10,
        topic_name="technology",
    )

    assert total == 1
    assert len(feed) == 1
    assert feed[0].title == "AI News"


async def test_user_feed_filter_by_source_name(db_session):
    """Test filtering feed by source name."""

    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="test-user")

    topic = TopicModel(name="technology")

    bbc = SourceModel(
        name="BBC",
        base_url="https://bbc.com",
    )

    cnn = SourceModel(
        name="CNN",
        base_url="https://cnn.com",
    )

    db_session.add_all(
        [
            topic,
            bbc,
            cnn,
        ]
    )

    await db_session.flush()

    subscription_repo = SubscriptionRepo(db_session)

    await subscription_repo.create(
        user_id=user.id,
        topic_id=topic.id,
    )

    bbc_post = PostModel(
        title="BBC Tech",
        content="BBC content",
        url="https://bbc.com/tech",
        source_id=bbc.id,
        topics=[topic],
    )

    cnn_post = PostModel(
        title="CNN Tech",
        content="CNN content",
        url="https://cnn.com/tech",
        source_id=cnn.id,
        topics=[topic],
    )

    db_session.add_all(
        [
            bbc_post,
            cnn_post,
        ]
    )

    await db_session.commit()

    feed_repo = FeedRepo(db_session)

    total, feed = await feed_repo.user_feed(
        user_id=user.id,
        offset=0,
        limit=10,
        source_name="BBC",
    )

    assert total == 1
    assert len(feed) == 1
    assert feed[0].title == "BBC Tech"


async def test_user_feed_search(db_session):
    """Test feed search functionality."""

    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="test-user")

    topic = TopicModel(name="technology")

    source = SourceModel(
        name="BBC",
        base_url="https://bbc.com",
    )

    db_session.add_all(
        [
            topic,
            source,
        ]
    )

    await db_session.flush()

    subscription_repo = SubscriptionRepo(db_session)

    await subscription_repo.create(
        user_id=user.id,
        topic_id=topic.id,
    )

    ai_post = PostModel(
        title="AI Revolution",
        content="Artificial intelligence breakthrough",
        url="https://bbc.com/ai",
        source_id=source.id,
        topics=[topic],
    )

    sports_post = PostModel(
        title="Football News",
        content="Match updates",
        url="https://bbc.com/football",
        source_id=source.id,
        topics=[topic],
    )

    db_session.add_all(
        [
            ai_post,
            sports_post,
        ]
    )

    await db_session.commit()

    feed_repo = FeedRepo(db_session)

    total, feed = await feed_repo.user_feed(
        user_id=user.id,
        offset=0,
        limit=10,
        search="AI",
    )

    assert total == 1
    assert len(feed) == 1
    assert feed[0].title == "AI Revolution"


async def test_user_feed_pagination(db_session):
    """Test feed pagination."""

    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="test-user")

    topic = TopicModel(name="technology")

    source = SourceModel(
        name="BBC",
        base_url="https://bbc.com",
    )

    db_session.add_all(
        [
            topic,
            source,
        ]
    )

    await db_session.flush()

    subscription_repo = SubscriptionRepo(db_session)

    await subscription_repo.create(
        user_id=user.id,
        topic_id=topic.id,
    )

    for index in range(5):
        post = PostModel(
            title=f"Post {index}",
            content=f"Content {index}",
            url=f"https://bbc.com/post-{index}",
            source_id=source.id,
            topics=[topic],
        )

        db_session.add(post)

    await db_session.commit()

    feed_repo = FeedRepo(db_session)

    total, feed = await feed_repo.user_feed(
        user_id=user.id,
        offset=0,
        limit=2,
    )

    assert total == 5
    assert len(feed) == 2


async def test_user_feed_excludes_deleted_posts(db_session):
    """Test deleted posts are excluded from feed."""

    user_repo = UserRepository(db_session)
    user = await user_repo.create(username="test-user")

    topic = TopicModel(name="technology")

    source = SourceModel(
        name="BBC",
        base_url="https://bbc.com",
    )

    db_session.add_all(
        [
            topic,
            source,
        ]
    )

    await db_session.flush()

    subscription_repo = SubscriptionRepo(db_session)

    await subscription_repo.create(
        user_id=user.id,
        topic_id=topic.id,
    )

    deleted_post = PostModel(
        title="Deleted News",
        content="Should not appear",
        url="https://bbc.com/deleted",
        source_id=source.id,
        is_deleted=True,
        topics=[topic],
    )

    db_session.add(deleted_post)

    await db_session.commit()

    feed_repo = FeedRepo(db_session)

    total, feed = await feed_repo.user_feed(
        user_id=user.id,
        offset=0,
        limit=10,
    )

    assert total == 0
    assert len(feed) == 0
