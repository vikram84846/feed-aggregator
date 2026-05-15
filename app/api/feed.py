"""
This module lists the routes associated to feed
currently it contains:
    - /api/v1/feed

"""

from fastapi import Depends, APIRouter, status
from app.services.feed import FeedService
from app.db.db import get_async_session
from app.utils.dependency import get_current_user
from app.schema.pagination_schema import PaginatedResponse
from app.schema.feed_schema import FeedQueryParams, PostResponse
from app.models.users import UserModel
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/feed", tags=["UserFeed"])


@router.get("/", response_model=PaginatedResponse[PostResponse], status_code=status.HTTP_200_OK)
async def user_feed(
    query: FeedQueryParams = Depends(),
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    generates user personalised feed
    """
    feed_service = FeedService(session)
    return await feed_service.get_user_feed(
        current_user.id,
        query.page,
        query.limit,
        query.search,
        query.topic_name,
        query.source_name,
    )
