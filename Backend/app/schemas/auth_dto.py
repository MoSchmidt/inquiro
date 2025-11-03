"""Pydantic models for authentication requests and responses."""

from typing import Any, Dict

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Payload for authenticating a user."""

    username: str


class LoginResponse(BaseModel):
    """Response returned after a successful login."""

    access_token: str
    refresh_token: str
    token_type: str
    user: Dict[str, Any]


class RefreshRequest(BaseModel):
    """Payload containing the refresh token."""

    refresh_token: str


class RefreshResponse(BaseModel):
    """Response containing a fresh access token."""

    access_token: str
    token_type: str
