import pytest_asyncio
from app.models.base import Base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


TEST_DB_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DB_URL)


AsyncTestSessionLocal = async_sessionmaker(engine)


@pytest_asyncio.fixture()
async def db_session():

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncTestSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
