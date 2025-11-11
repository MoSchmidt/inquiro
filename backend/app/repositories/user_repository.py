from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Repository for user-related database operations."""

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """Fetch a user by username."""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def exists(db: Session, username: str) -> bool:
        """Check whether a user exists."""
        return db.query(User).filter(User.username == username).first() is not None

    @staticmethod
    def create(db: Session, username: str) -> User:
        """Create a new user."""
        user = User(username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
