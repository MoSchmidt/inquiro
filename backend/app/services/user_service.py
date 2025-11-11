from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository


class UserService:
    """Service for user management."""

    @staticmethod
    def create_user(db: Session, username: str) -> User:
        """Create a user if the username is free."""

        if UserRepository.exists(db, username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )
        return UserRepository.create(db, username)

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User:
        """Fetch a user by username."""
        user = UserRepository.get_by_username(db, username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        return user
