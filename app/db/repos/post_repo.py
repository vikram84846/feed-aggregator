"""
Post repository for database operations related to Post .

Responsibilities:
    - create Post and Topic
    - fetch Post, Topic by id/name/title
    - soft delete Topics and Posts

NOTE:
    - Repository layer should remain dumb.
    - No commits inside repository.
    - Transaction lifecycle handled by service layer.
"""

from sqlalchemy import select, func

from app.db.repos.base_repo import BaseRepository
from app.models.posts import TopicModel, PostModel


class TopicRepository(BaseRepository):
    async def get_by_id(
        self, topic_id: str, include_deleted: bool = False
    ) -> TopicModel | None:
        """
        fetches the topic using its id from database
        Args:
            - topic_id: unique identifer for topic
            - include_deleted: flag to include delted topics

        """
        stmt = select(TopicModel).where(TopicModel.id == topic_id)

        if not include_deleted:
            stmt = stmt.where(TopicModel.is_deleted.is_(False))

        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(
        self, topic_name: str, include_deleted: bool = False
    ) -> TopicModel | None:
        """
        fetches the topic using its name from database
        Args:
            - topic_name: name of the topic
            - include_deleted: flag to include delted topics

        """
        stmt = select(TopicModel).where(TopicModel.name == topic_name)

        if not include_deleted:
            stmt = stmt.where(TopicModel.is_deleted.is_(False))

        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, topic_name: str) -> TopicModel:
        """
        create a new topic record in database
        Args:
            - topic_name: unique name for the topic
        """
        topic = TopicModel(name=topic_name)

        self._session.add(topic)
        await self._session.flush()
        await self._session.refresh(topic)
        return topic

    async def delete(self, topic_id: str) -> TopicModel | None:
        """
        soft delete the topic.
        Args:
            - topic_id: unique identifer for the topic
        """

        topic = await self.get_by_id(topic_id=topic_id, include_deleted=True)

        if not topic:
            return None

        topic.is_deleted = True
        await self._session.flush()
        return topic

    async def get_subscribed_users(
        self, topic_id: str, include_deleted: bool = False
    ) -> list[str] | None:
        """
        lists the users subscribed to topic
        Args:
            - topic_id : unique identifier for topic
            - include_deleted : includes soft delted values
        """
        from app.models.users import UserModel, TopicSubscriptionModel

        stmt = (
            select(UserModel)
            .join(TopicSubscriptionModel)
            .where(TopicSubscriptionModel.topic_id == topic_id)
        )
        if not include_deleted:
            stmt = stmt.where(TopicSubscriptionModel.is_deleted.is_(False))

        result = await self._session.execute(stmt)
        users = result.scalars().all()
        if users:
            return [user.username for user in users]
        topic = await self.get_by_id(topic_id=topic_id)
        if not topic:
            return None

        return []


class PostRepository(BaseRepository):
    async def get_by_id(
        self, post_id: str, include_deleted: bool = False
    ) -> PostModel | None:
        """
        return the post record form database
        Args:
            - post_id: unique post identifeir
            - include_deleted: include soft delted posts
        """

        stmt = select(PostModel).where(PostModel.id == post_id)

        if not include_deleted:
            stmt = stmt.where(PostModel.is_deleted.is_(False))

        post = await self._session.execute(stmt)
        return post.scalar_one_or_none()

    async def get_by_title(
        self,
        post_title: str,
        offset: int = 0,
        limit: int = 10,
        include_deleted: bool = False,
    ) -> tuple[int, list[PostModel]]:
        """
        fetches the post record(s) filtered by name
        Args:
            - post_title: title of the post(s)
            - include_deleted: inculde soft deleted posts
            - offset: no of post to skip
            - limit: no of post to fetch
        """

        # fetch the posts statement
        base_stmt = select(PostModel).where(PostModel.title == post_title)

        if not include_deleted:
            base_stmt = base_stmt.where(PostModel.is_deleted.is_(False))

        total_posts = await self._session.scalar(
            select(func.count()).select_from(base_stmt.subquery())
        )

        post_stmt = (
            base_stmt.order_by(PostModel.created_at.desc(), PostModel.id.desc())
            .offset(offset)
            .limit(limit)
        )

        q = await self._session.execute(post_stmt)
        posts = q.scalars().all()

        return (total_posts, posts)

    async def create(
        self, title: str, content: str, url: str, source_id: str
    ) -> PostModel:
        """
        create a post record in the database
        Args:
            - title: title for post
            - content: content for post
            - url:str unique url for post identification
            - source_id: id of source that generated the post
        """

        post = PostModel(title=title, content=content, url=url, source_id=source_id)
        self._session.add(post)
        await self._session.flush()
        await self._session.refresh(post)
        return post

    async def delete(self, post_id: str) -> PostModel | None:
        """
        soft deletes the post record from databse
        Args:
            - post_id: unique post identifier
        """
        post = await self.get_by_id(post_id=post_id, include_deleted=True)
        if not post:
            return
        post.is_deleted = True
        await self._session.flush()
        return post
