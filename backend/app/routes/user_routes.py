"""Routes for managing and retrieving user information."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user_dto import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


class UserCreate(BaseModel):
    """Payload used when creating a new user."""

    username: str


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(request: UserCreate, db: Session = Depends(get_db)) -> User:
    """Create a new user record if the username is available."""

    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    user = User(username=request.username)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_current_user_profile(
    current_username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """Return the user information for the authenticated principal."""

    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return user
