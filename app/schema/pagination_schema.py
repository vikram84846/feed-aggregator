from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool
    next_page: int | None
    previous_page: int | None


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: PaginationMeta
