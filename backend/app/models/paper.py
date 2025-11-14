"""SQLAlchemy model and enumerations for scholarly papers."""

from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import JSON, BigInteger, Date, DateTime, String, Text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.constants.database_constants import PaperSource, PaperType
from app.core.database import Base


class Paper(Base):
    """Database representation of a scholarly paper."""

    __tablename__ = "paper"

    paper_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    doi: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    source: Mapped[PaperSource] = mapped_column(
        SqlEnum(PaperSource, name="paper_source"), nullable=False
    )
    paper_type: Mapped[PaperType] = mapped_column(
        SqlEnum(PaperType, name="paper_type"),
        nullable=False,
        default=PaperType.PREPRINT,
        server_default=PaperType.PREPRINT.value,
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    authors: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    published_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    pdf_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    project_links: Mapped[List["ProjectPaper"]] = relationship(
        "ProjectPaper", back_populates="paper", cascade="all, delete-orphan"
    )
    projects: Mapped[List["Project"]] = relationship(
        "Project", secondary="project_paper", back_populates="papers"
    )


if TYPE_CHECKING:
    from .project import Project
    from .project_paper import ProjectPaper
