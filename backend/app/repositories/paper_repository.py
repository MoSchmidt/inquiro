from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Paper


class PaperRepository:
    """Repository for paper-related database operations"""

    @staticmethod
    async def get_paper_by_id(session: AsyncSession, paper_id: int) -> Paper:
        """
        Returns a paper identified by its id
        """
        stmt = select(Paper).where(Paper.paper_id == paper_id)
        result = await session.scalars(stmt)
        return result.first()
