from app.db.repos.source_repo import SourceRepository


async def test_source_create(db_session):
	repo = SourceRepository(db_session)
	source = await repo.create("test-source", "http://test-url.com")
	assert source.id is not None
	assert source.name == "test-source"
	assert source.base_url == "http://test-url.com"
	assert source.is_deleted is False

async def test_get_by_id(db_session):
	repo = SourceRepository(db_session)
	source = await repo.create("source-by-id", "http://url-by-id.com")
	source_id = source.id
	fetched = await repo.get_by_id(source_id)
	assert fetched is not None
	assert fetched.id == source_id
	assert fetched.name == "source-by-id"

async def test_get_by_base_url(db_session):
	repo = SourceRepository(db_session)
	source = await repo.create("source-by-url", "http://url-by-url.com")
	fetched = await repo.get_by_base_url("http://url-by-url.com")
	assert fetched is not None
	assert fetched.name == "source-by-url"

async def test_source_delete(db_session):
	repo = SourceRepository(db_session)
	source = await repo.create("source-to-delete", "http://delete-url.com")
	source_id = source.id
	deleted = await repo.delete(source_id)
	assert deleted.is_deleted is True
	# Should not return in normal get
	assert await repo.get_by_id(source_id) is None
	# Should return if include_deleted=True
	assert await repo.get_by_id(source_id, include_deleted=True) is not None

async def test_get_by_id_not_found(db_session):
	repo = SourceRepository(db_session)
	assert await repo.get_by_id("non-existent-id") is None

async def test_get_by_base_url_not_found(db_session):
	repo = SourceRepository(db_session)
	assert await repo.get_by_base_url("http://no-such-url.com") is None

async def test_delete_not_found(db_session):
	repo = SourceRepository(db_session)
	assert await repo.delete("non-existent-id") is None
