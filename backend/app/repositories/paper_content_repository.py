from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.database_constants import PaperContentStatus
from app.models.paper_content import PaperContent


class PaperContentRepository:
    """Repository for paper content database operations."""

    @staticmethod
    async def get_by_paper_id(session: AsyncSession, paper_id: int) -> Optional[PaperContent]:
        """Returns paper content for the specified paper, or None if not found."""
        stmt = (
            select(PaperContent)
            .where(PaperContent.paper_id == paper_id)
            .execution_options(populate_existing=True)
        )
        result = await session.scalars(stmt)
        return result.first()

    @staticmethod
    async def create_pending(session: AsyncSession, paper_id: int) -> PaperContent:
        """Creates a new PaperContent record with PENDING status."""
        content = PaperContent(
            paper_id=paper_id,
            status=PaperContentStatus.PENDING,
        )
        session.add(content)
        await session.commit()
        await session.refresh(content)
        return content

    @staticmethod
    async def get_or_create_pending(
        session: AsyncSession, paper_id: int
    ) -> tuple[PaperContent, bool]:
        """
        Gets existing PaperContent or creates a new one with PENDING status.
        Returns tuple of (content, created) where created is True if newly created.
        """
        existing = await PaperContentRepository.get_by_paper_id(session, paper_id)
        if existing:
            return existing, False
        content = await PaperContentRepository.create_pending(session, paper_id)
        return content, True
