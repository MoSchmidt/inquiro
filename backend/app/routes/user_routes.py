from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.schemas.user_dto import UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
async def create_user(request: UserCreate, db: AsyncSession = Depends(get_db)) -> UserResponse:
    """Create a new user."""

    user = await UserService.create_user(db, request.username)
    return UserResponse.model_validate(user)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the current user's profile",
)
async def get_current_user_profile(
        current_user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Return the authenticated user's profile."""

    user = await UserService.get_user_by_user_id(db, current_user_id)
    return UserResponse.model_validate(user)
