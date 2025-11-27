from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository


class UserService:
    """Service for user management."""

    @staticmethod
    async def create_user(db: AsyncSession, username: str) -> User:
        """Create a user if the username is free."""

        if await UserRepository.exists(db, username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )
        return await UserRepository.create(db, username)

    @staticmethod
    async def get_user_by_user_id(db: AsyncSession, user_id: int) -> User:
        """Fetch a user by username."""
        user = await UserRepository.get_by_user_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        return user
