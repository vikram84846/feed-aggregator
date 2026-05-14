import asyncio
from app.models.posts import TopicModel
from app.db.db import async_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


async def add_topics(session: AsyncSession):
    topic1 = TopicModel(name="Python")
    t2 = TopicModel(name="AI")
    t3 = TopicModel(name="DataScience")

    session.add(topic1)
    session.add(t2)
    session.add(t3)
    await session.flush()


async def main():
    AsyncLocalSession = async_sessionmaker(
        async_engine, autoflush=True, autocommit=False
    )

    async with AsyncLocalSession() as session:
        await add_topics(session)
        await session.commit()


asyncio.run(main())
