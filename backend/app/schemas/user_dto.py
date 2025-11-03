"""Pydantic models for user-facing responses."""

from pydantic import BaseModel


class UserResponse(BaseModel):
    """Representation of a user returned by the API."""

    id: int
    username: str

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic configuration options."""

        from_attributes = True  # For Pydantic v2
