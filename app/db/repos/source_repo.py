"""
Source repository for database operations related to Post .

Responsibilities:
    - create source
    - fetch source by id/name
    - soft delete source

NOTE:
    - Repository layer should remain dumb.
    - No commits inside repository.
    - Transaction lifecycle handled by service layer.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repos.base_repo import BaseRepository
from app.models.sources import SourceModel


class SourceRepository(BaseRepository):

    async def get_by_id(
        self, source_id: str, include_deleted: bool = False
    ) -> SourceModel | None:
        """
        fetches the source record from database
        Args:
            - source_id: unique identifier for source
            - include_deleted: include soft deleted sources
        """
        stmt = select(SourceModel).where(SourceModel.id == source_id)

        if not include_deleted:
            stmt = stmt.where(SourceModel.is_deleted.is_(False))

        source = await self._session.execute(stmt)
        return source.scalar_one_or_none()

    async def get_by_base_url(
        self, base_url: str, include_deleted: bool = False
    ) -> SourceModel | None:
        """
        fetches the source record from database
        Args:
            - base_url: base url for source
            - include_deleted: include soft deleted sources
        """
        stmt = select(SourceModel).where(SourceModel.base_url == base_url)

        if not include_deleted:
            stmt = stmt.where(SourceModel.is_deleted.is_(False))

        source = await self._session.execute(stmt)
        return source.scalar_one_or_none()

    async def create(self, name: str, base_url: str) -> SourceModel | None:
        """
        creates a post generation source record in database
        Args:
            - name: unique name for source
            - url: unique url for source
        """

        source = SourceModel(name=name, base_url=base_url)
        self._session.add(source)
        await self._session.flush()
        await self._session.refresh(source)
        return source

    async def delete(self, source_id: str) -> SourceModel | None:
        """
        soft deletes the source record from database
        Args:
            - source_id: unique identifier for source
        """

        source = await self.get_by_id(source_id=source_id, include_deleted=True)
        if not source:
            return
        source.is_deleted = True
        await self._session.flush()
        return source
