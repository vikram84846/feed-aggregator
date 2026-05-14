"""
Feed repository for querying database posts as per user personalisation.

Responsibilities:
    - Fetch posts for a user's feed
    - Filter posts by subscribed topics
    - Support filtering by topic and source
    - Support keyword-based search
    - Return paginated results ordered by newest first
"""

from sqlalchemy import func, or_, select

from app.db.repos.base_repo import BaseRepository
from app.models.posts import PostModel, PostTopicModel, TopicModel
from app.models.sources import SourceModel
from app.models.users import TopicSubscriptionModel


class FeedRepo(BaseRepository):
    """Repository for handling user feed queries."""

    async def user_feed(
        self,
        user_id: str,
        offset: int,
        limit: int,
        topic_name: str | None = None,
        source_name: str | None = None,
        search: str | None = None,
    ) -> tuple[int, list[PostModel]]:
        """
        Fetch a personalised feed for a user.

        The feed contains posts associated with topics the user is
        subscribed to. Results can optionally be filtered by topic,
        source, or a search keyword.

        Args:
            user_id: Unique identifier of the user.
            offset: Number of records to skip for pagination.
            limit: Maximum number of records to return.
            topic_name: Optional topic name filter.
            source_name: Optional source name filter.
            search: Optional keyword used to search across:
                - post title
                - post content
                - topic name

        Returns:
            A tuple containing:
                - total count of matching posts
                - list of paginated PostModel objects

        Notes:
            - Soft-deleted records are excluded.
            - Posts are ordered by newest first.
            - DISTINCT is used to avoid duplicate posts caused by joins.
        """

        base_stmt = (
            select(PostModel)
            .distinct()
            .join(
                PostTopicModel,
                PostModel.id == PostTopicModel.post_id,
            )
            .join(
                TopicSubscriptionModel,
                TopicSubscriptionModel.topic_id == PostTopicModel.topic_id,
            )
            .where(
                TopicSubscriptionModel.user_id == user_id,
                TopicSubscriptionModel.is_deleted.is_(False),
                PostModel.is_deleted.is_(False),
                PostTopicModel.is_deleted.is_(False),
            )
        )

        # Join TopicModel only once if topic-related filters are required
        if search or topic_name:
            base_stmt = base_stmt.join(
                TopicModel,
                TopicModel.id == PostTopicModel.topic_id,
            )

        # Apply keyword search filters
        if search:
            base_stmt = base_stmt.where(
                or_(
                    PostModel.title.ilike(f"%{search}%"),
                    PostModel.content.ilike(f"%{search}%"),
                    TopicModel.name.ilike(f"%{search}%"),
                )
            )

        # Filter by topic name
        if topic_name:
            base_stmt = base_stmt.where(TopicModel.name == topic_name)

        # Filter by source name
        if source_name:
            base_stmt = base_stmt.join(
                SourceModel,
                SourceModel.id == PostModel.source_id,
            ).where(SourceModel.name == source_name)

        # Query for total matching records
        count_query = select(func.count()).select_from(base_stmt.subquery())

        # Final paginated query
        final_query = (
            base_stmt.order_by(
                PostModel.created_at.desc(),
                PostModel.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        total = await self._session.scalar(count_query)

        posts = await self._session.execute(final_query)

        feed = posts.scalars().all()

        return total, feed
