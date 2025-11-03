"""Routes related to authentication and JWT management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.models.user import User
from app.schemas.auth_dto import (
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RefreshResponse,
)
from app.schemas.user_dto import UserResponse


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
    summary="Authenticate a user and return JWT tokens",
)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    """Authenticate a user and return access plus refresh tokens."""

    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username.",
        )

    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})

    user_dto = UserResponse.model_validate(user)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user_dto.model_dump(),
    )


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=RefreshResponse,
    summary="Generate a new access token using a refresh token",
)
def refresh_access_token(request: RefreshRequest) -> RefreshResponse:
    """Validate a refresh token and return a new access token."""

    payload = verify_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    username = payload.get("sub")
    new_access_token = create_access_token({"sub": username})

    return RefreshResponse(access_token=new_access_token, token_type="bearer")
