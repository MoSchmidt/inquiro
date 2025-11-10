from pydantic import BaseModel

from app.schemas.user_dto import UserResponse


class LoginRequest(BaseModel):
    """Payload for authenticating a user."""

    username: str


class LoginResponse(BaseModel):
    """Response returned after a successful login."""

    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse


class RefreshRequest(BaseModel):
    """Payload containing the refresh token."""

    refresh_token: str


class RefreshResponse(BaseModel):
    """Response containing a fresh access token."""

    access_token: str
    token_type: str
