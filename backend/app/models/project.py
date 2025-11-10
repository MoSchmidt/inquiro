"""SQLAlchemy model for projects managed in the application."""

# pylint: disable=too-few-public-methods

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Project(Base):
    """Database representation of a user project."""

    __tablename__ = "project"

    project_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    created_by: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("user.user_id"), nullable=False, index=True
    )
    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    creator: Mapped["User"] = relationship("User", back_populates="projects")
    project_papers: Mapped[List["ProjectPaper"]] = relationship(
        "ProjectPaper", back_populates="project", cascade="all, delete-orphan"
    )
    papers: Mapped[List["Paper"]] = relationship(
        "Paper", secondary="project_paper", back_populates="projects"
    )

if TYPE_CHECKING:
    from .paper import Paper
    from .project_paper import ProjectPaper
    from .user import User
