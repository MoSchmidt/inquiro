from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.security import create_access_token, create_refresh_token, verify_token
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    """Service for authentication and token handling."""

    @staticmethod
    def login(db: AsyncSession, username: str) -> tuple[User, str, str]:
        """Authenticate a user and create JWT tokens."""

        user = UserRepository.get_by_username(db, username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username."
            )

        access_token = create_access_token({"sub": user.username})
        refresh_token = create_refresh_token({"sub": user.username})

        return user, access_token, refresh_token

    @staticmethod
    def refresh(refresh_token: str) -> str:
        """Generate a new access token from a refresh token."""

        payload = verify_token(refresh_token)

        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        username = payload["sub"]
        return create_access_token({"sub": username})
