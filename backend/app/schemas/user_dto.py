from pydantic import BaseModel


class UserCreate(BaseModel):
    """Request to create a new user."""

    username: str

class UserResponse(BaseModel):
    """Representation of a user returned by the API."""

    user_id: int
    username: str

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic configuration options."""

        from_attributes = True  # For Pydantic v2
