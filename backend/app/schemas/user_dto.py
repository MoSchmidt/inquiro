"""Pydantic models for user-facing responses."""

from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    """Representation of a user returned by the API."""

    user_id: int
    username: str
    created_at: datetime

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic configuration options."""

        from_attributes = True  # For Pydantic v2
