"""
User repository for database operations related to users.

Responsibilities:
    - create users
    - fetch users by id/email/username
    - soft delete users

NOTE:
    - Repository layer should remain dumb.
    - No commits inside repository.
    - Transaction lifecycle handled by service layer.
"""

from sqlalchemy import select, or_

from app.db.repos.base_repo import BaseRepository
from app.models.users import UserModel


class UserRepository(BaseRepository):
    async def get_by_email(
        self, email: str, include_deleted: bool = False
    ) -> UserModel | None:
        """
        Fetch user using email.

        Args:
            email: user's unique email
            include_deleted: include soft deleted users

        Returns:
            UserModel | None
        """

        stmt = select(UserModel).where(UserModel.email == email)

        if not include_deleted:
            stmt = stmt.where(UserModel.is_deleted.is_(False))

        result = await self._session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by_id(
        self, user_id: str, include_deleted: bool = False
    ) -> UserModel | None:
        """
        Fetch user using user id.

        Args:
            user_id: unique user id
            include_deleted: include soft deleted users

        Returns:
            UserModel | None
        """

        stmt = select(UserModel).where(UserModel.id == user_id)

        if not include_deleted:
            stmt = stmt.where(UserModel.is_deleted.is_(False))

        result = await self._session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by_username(
        self, username: str, include_deleted: bool = False
    ) -> UserModel | None:
        """
        Fetch user using username.

        Args:
            username: unique username
            include_deleted: include soft deleted users

        Returns:
            UserModel | None
        """

        stmt = select(UserModel).where(UserModel.username == username)

        if not include_deleted:
            stmt = stmt.where(UserModel.is_deleted.is_(False))

        result = await self._session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by_email_or_username(
        self, username: str, email: str, include_deleted: bool = False
    ) -> UserModel | None:
        """
        Fetch user using username or email.

        Args:
            username: unique username
            email: unique email
            include_deleted: include soft deleted users

        Returns:
            UserModel | None
        """

        stmt = select(UserModel).where(
            or_(UserModel.username == username, UserModel.email == email)
        )

        if not include_deleted:
            stmt = stmt.where(UserModel.is_deleted.is_(False))

        result = await self._session.execute(stmt)

        return result.scalar_one_or_none()

    async def create(
        self, username: str, password_hash: str | None = None, email: str | None = None
    ) -> UserModel:
        """
        Create a new user record.

        Args:
            username: unique username
            password_hash: hashed password
            email: unique email

        Returns:
            Created UserModel object
        """

        user = UserModel(username=username, password_hash=password_hash, email=email)

        self._session.add(user)

        await self._session.flush()
        await self._session.refresh(user)

        return user

    async def delete(self, user_id: str) -> UserModel | None:
        """
        Soft delete a user.

        Args:
            user_id: unique user id

        Returns:
            Updated UserModel | None
        """

        user = await self.get_by_id(user_id=user_id, include_deleted=True)

        if not user:
            return None

        user.is_deleted = True

        await self._session.flush()

        return user

    async def get_subscribed_topics(
        self, user_id: str, include_deleted: bool = False
    ) -> list[str] | None:
        """
        lists the topics subscribed by user
        Args:
            - user_id : unique identifier for user
            - include_deleted : includes soft deleted topics
        """
        # import inside method to avoid circular imports
        from app.models.posts import TopicModel
        from app.models.users import TopicSubscriptionModel

        stmt = (
            select(TopicModel)
            .join(TopicSubscriptionModel)
            .where(TopicSubscriptionModel.user_id == user_id)
        )
        if not include_deleted:
            stmt = stmt.where(TopicSubscriptionModel.is_deleted.is_(False))
        result = await self._session.execute(stmt)

        topics = result.scalars().all()
        if topics:
            return [topic.name for topic in topics]

        user = await self.get_by_id(user_id=user_id)
        if not user:
            return None

        return []
