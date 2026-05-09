from app.db.repos.post_repo import PostRepository


async def test_post_create(db_session):
    post = PostRepository(db_session)
    test_post = await post.create(
        "test-title", "test-content", "test-url", "test-source"
    )
    assert test_post.id is not None
    assert test_post.title == "test-title"
    assert test_post.content == "test-content"
    assert test_post.url == "test-url"
    assert test_post.source_id == "test-source"
    assert test_post.is_deleted is False


async def test_get_by_id(db_session):
    post_repo = PostRepository(db_session)
    test_post = await post_repo.create(
        "test-title", "test-content", "test-url", "test-source"
    )
    post_id = test_post.id

    post = await post_repo.get_by_id(post_id)

    assert post.id == post_id
    assert post.title == "test-title"
    assert post.content == "test-content"
    assert post.url == "test-url"
    assert post.source_id == "test-source"
    assert post.is_deleted is False


async def test_get_by_title(db_session):
    post_repo = PostRepository(db_session)
    await post_repo.create("test-title", "test-content", "test-url-0", "test-source")
    await post_repo.create("test-title", "test-content", "test-url-1", "test-source")
    await post_repo.create("test-title", "test-content", "test-url-2", "test-source")

    count, posts = await post_repo.get_by_title("test-title")
    assert count == 3
    assert len(posts) == 3


async def test_get_by_id_not_found(db_session):
    post_repo = PostRepository(db_session)
    assert await post_repo.get_by_id("non-existent-id") is None


async def test_get_by_title_not_found(db_session):
    post_repo = PostRepository(db_session)
    count, posts = await post_repo.get_by_title("no-such-title")
    assert count == 0
    assert posts == []


async def test_post_delete_not_found(db_session):
    post_repo = PostRepository(db_session)
    assert await post_repo.delete("non-existent-id") is None


async def test_post_delete_and_include_deleted(db_session):
    post_repo = PostRepository(db_session)
    test_post = await post_repo.create(
        "del-title", "del-content", "del-url", "del-source"
    )
    post_id = test_post.id
    await post_repo.delete(post_id)
    # Should not return in normal get
    assert await post_repo.get_by_id(post_id) is None
    # Should return if include_deleted=True
    assert await post_repo.get_by_id(post_id, include_deleted=True) is not None


async def test_get_by_title_include_deleted(db_session):
    post_repo = PostRepository(db_session)
    p1 = await post_repo.create("del-title", "content", "url-1", "source")
    await post_repo.create("del-title", "content", "url-2", "source")
    await post_repo.delete(p1.id)
    count, posts = await post_repo.get_by_title("del-title")
    assert count == 1
    assert len(posts) == 1
    count_all, posts_all = await post_repo.get_by_title(
        "del-title", include_deleted=True
    )
    assert count_all == 2
    assert len(posts_all) == 2


async def test_post_delete(db_session):
    post_repo = PostRepository(db_session)
    test_post = await post_repo.create(
        "test-title", "test-content", "test-url", "test-source"
    )
    post_id = test_post.id

    post = await post_repo.delete(post_id)
    assert post.is_deleted is True
