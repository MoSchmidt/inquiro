from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth_dto import LoginRequest, LoginResponse, RefreshRequest, RefreshResponse
from app.schemas.user_dto import UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate a user and return JWT tokens"
)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate a user and return access plus refresh tokens."""

    user, access_token, refresh_token = AuthService.login(db, request.username)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a new access token using a refresh token"
)
def refresh_access_token(request: RefreshRequest) -> RefreshResponse:
    """Validate a refresh token and return a new access token."""

    new_access_token = AuthService.refresh(request.refresh_token)

    return RefreshResponse(
        access_token=new_access_token,
        token_type="bearer",
    )
