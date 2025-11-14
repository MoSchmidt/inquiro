"""Association table model linking projects and papers."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ProjectPaper(Base):
    """Associative entity connecting projects with papers."""

    __tablename__ = "project_paper"

    # Ensure a paper can only be linked once to the same project.
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "paper_id",
            name="uq_project_paper_project_id_paper_id",
        ),
    )

    project_paper_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    project_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("project.project_id"), nullable=False, index=True)

    paper_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("paper.paper_id"), nullable=False, index=True)

    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    project: Mapped["Project"] = relationship("Project", back_populates="project_papers")
    paper: Mapped["Paper"] = relationship("Paper", back_populates="project_links")


if TYPE_CHECKING:
    from .paper import Paper
    from .project import Project
