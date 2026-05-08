from app.db.repos.post_repo import TopicRepository
import pytest

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
	topic = await topic_repo.create("topic-by-name")
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
