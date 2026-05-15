"""
This service generates the posts feed personalised to user
feed generation supports:
- filtering by topic and source
- keyword-based search
- Return paginated results ordered by newest first
"""

from app.db.repos.feed_repo import FeedRepo
from sqlalchemy.ext.asyncio import AsyncSession
import math
from app.schema.pagination_schema import PaginatedResponse, PaginationMeta


class FeedService:
    def __init__(self, session: AsyncSession):
        """
        Initailises the feed service with feed repository
            Args:
            session : async db session object
        """
        self._feed_repo = FeedRepo(session)

    async def get_user_feed(
        self,
        user_id,
        page: int,
        limit: int,
        search: str = None,
        topic_name: str = None,
        source_name: str = None,
    ):
        """
        This method generates user personalised feed (contaning articles )for the topic that user has subscribed
        Args:
            - user_id : unique identifier for user
            - page : int value of page to be fetched
            -
        """
        offset = (page - 1) * limit
        count, items = await self._feed_repo.user_feed(
            user_id, offset, limit, topic_name, source_name, search
        )
        total_pages = max(math.ceil(count / limit), 1)
        meta = PaginationMeta(
            page=page,
            limit=limit,
            total_items=count,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
            next_page=page + 1 if page < total_pages else None,
            previous_page=page - 1 if page > 1 else None,
        )
        return PaginatedResponse(data=items, meta=meta)
