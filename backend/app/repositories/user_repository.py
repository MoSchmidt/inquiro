from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """Repository for user-related database operations."""

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Fetch a user by username."""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def exists(db: AsyncSession, username: str) -> bool:
        """Check whether a user exists."""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def create(db: AsyncSession, username: str) -> User:
        """Create a new user."""
        user = User(username=username)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
