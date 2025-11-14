from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.user_dto import UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
def create_user(request: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    """Create a new user."""

    user = UserService.create_user(db, request.username)
    return UserResponse.model_validate(user)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the current user's profile",
)
def get_current_user_profile(
    current_username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    """Return the authenticated user's profile."""

    user = UserService.get_user_by_username(db, current_username)
    return UserResponse.model_validate(user)
