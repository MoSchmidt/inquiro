from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, verify_token
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    """Service for authentication and token handling."""

    @staticmethod
    async def login(db: AsyncSession, username: str) -> tuple[User, str, str]:
        """Authenticate a user and create JWT tokens."""

        user = await UserRepository.get_by_username(db, username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username."
            )

        access_token = create_access_token({"sub": str(user.user_id)})
        refresh_token = create_refresh_token({"sub": str(user.user_id)})

        return user, access_token, refresh_token

    @staticmethod
    async def refresh(refresh_token: str) -> str:
        """Generate a new access token from a refresh token."""

        payload = verify_token(refresh_token)

        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        user_id = payload["sub"]
        return create_access_token({"sub": str(user_id)})
