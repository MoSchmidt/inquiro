from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, ForeignKey, func, DateTime, Integer, Text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants.database_constants import PaperContentStatus
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.paper import Paper


class PaperContent(Base):
    __tablename__ = "paper_content"

    # Primary key
    paper_content_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True
    )

    # One-to-one FK to Paper
    paper_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("paper.paper_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Parsing state
    status: Mapped[PaperContentStatus] = mapped_column(
        SqlEnum(PaperContentStatus, name="paper_content_status"),
        nullable=False,
        default=PaperContentStatus.PENDING,
        server_default=PaperContentStatus.PENDING.value,
        index=True,
    )

    # Content
    markdown: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timing
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


    # Retry tracking
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    # Relationship
    paper: Mapped["Paper"] = relationship("Paper", back_populates="content")

