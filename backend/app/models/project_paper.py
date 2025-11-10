"""Association table model linking projects and papers."""

# pylint: disable=too-few-public-methods

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ProjectPaper(Base):
    """Associative entity connecting projects with papers."""

    __tablename__ = "project_paper"
    __table_args__ = (UniqueConstraint("project_id", "paper_id", name="uq_project_paper"),)

    project_paper_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("project.project_id"), nullable=False, index=True
    )
    paper_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("paper.paper_id"), nullable=False, index=True
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    project: Mapped["Project"] = relationship("Project", back_populates="project_papers")
    paper: Mapped["Paper"] = relationship("Paper", back_populates="project_links")


if TYPE_CHECKING:
    from .paper import Paper
    from .project import Project
