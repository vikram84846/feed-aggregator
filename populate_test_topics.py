import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from app.db.db import async_engine

from app.models.posts import (
    TopicModel,
    PostModel,
)

from app.models.sources import SourceModel


TOPICS = [
    "Python",
    "AI",
    "DataScience",
    "MachineLearning",
    "FastAPI",
    "Backend",
]

SOURCES = [
    {
        "name": "Real Python",
        "base_url": "https://realpython.com",
    },
    {
        "name": "Towards AI",
        "base_url": "https://towardsai.net",
    },
    {
        "name": "Analytics Vidhya",
        "base_url": "https://analyticsvidhya.com",
    },
]

POSTS = [
    {
        "title": "Getting Started with FastAPI",
        "content": "FastAPI is a modern Python web framework.",
        "url": "https://realpython.com/fastapi-start",
        "source": "Real Python",
        "topics": ["Python", "FastAPI", "Backend"],
    },
    {
        "title": "Understanding Neural Networks",
        "content": "Neural networks are the backbone of deep learning.",
        "url": "https://towardsai.net/neural-networks",
        "source": "Towards AI",
        "topics": ["AI", "MachineLearning", "DataScience"],
    },
    {
        "title": "Async IO in Python",
        "content": "Async IO enables concurrent programming in Python.",
        "url": "https://realpython.com/async-io-python",
        "source": "Real Python",
        "topics": ["Python", "Backend"],
    },
    {
        "title": "Pandas for Data Analysis",
        "content": "Pandas is powerful for working with tabular data.",
        "url": "https://analyticsvidhya.com/pandas-guide",
        "source": "Analytics Vidhya",
        "topics": ["Python", "DataScience"],
    },
    {
        "title": "Building ML APIs with FastAPI",
        "content": "Serve machine learning models using FastAPI.",
        "url": "https://towardsai.net/ml-fastapi",
        "source": "Towards AI",
        "topics": ["AI", "MachineLearning", "FastAPI", "Backend"],
    },
]


async def add_topics(session: AsyncSession):
    existing_topics_stmt = select(TopicModel)

    existing_topics_result = await session.execute(existing_topics_stmt)

    existing_topics = {topic.name for topic in existing_topics_result.scalars().all()}

    for topic_name in TOPICS:
        if topic_name not in existing_topics:
            session.add(TopicModel(name=topic_name))

    await session.flush()


async def add_sources(session: AsyncSession):
    existing_sources_stmt = select(SourceModel)

    existing_sources_result = await session.execute(existing_sources_stmt)

    existing_sources = {
        source.name for source in existing_sources_result.scalars().all()
    }

    for source_data in SOURCES:
        if source_data["name"] not in existing_sources:
            session.add(
                SourceModel(
                    name=source_data["name"],
                    base_url=source_data["base_url"],
                )
            )

    await session.flush()


async def add_posts(session: AsyncSession):
    topics_result = await session.execute(select(TopicModel))

    topics = {topic.name: topic for topic in topics_result.scalars().all()}

    sources_result = await session.execute(select(SourceModel))

    sources = {source.name: source for source in sources_result.scalars().all()}

    existing_posts_result = await session.execute(select(PostModel.url))

    existing_urls = {row[0] for row in existing_posts_result.all()}

    for post_data in POSTS:
        if post_data["url"] in existing_urls:
            continue

        source = sources.get(post_data["source"])

        post = PostModel(
            title=post_data["title"],
            content=post_data["content"],
            url=post_data["url"],
            source_id=source.id,
        )

        for topic_name in post_data["topics"]:
            topic = topics.get(topic_name)

            if topic:
                post.topics.append(topic)

        session.add(post)

    await session.flush()


async def main():
    AsyncLocalSession = async_sessionmaker(
        async_engine,
        autoflush=True,
        autocommit=False,
    )

    async with AsyncLocalSession() as session:
        await add_topics(session)

        await add_sources(session)

        await add_posts(session)

        await session.commit()

        print("Seed data inserted successfully")


asyncio.run(main())
