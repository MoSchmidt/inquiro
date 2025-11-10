"""SQLAlchemy model for application users."""

# pylint: disable=too-few-public-methods

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    """Database representation of an application user."""

    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    projects: Mapped[List["Project"]] = relationship(
        "Project", back_populates="creator", cascade="all, delete-orphan"
    )

if TYPE_CHECKING:  # pragma: no cover
    from .project import Project
