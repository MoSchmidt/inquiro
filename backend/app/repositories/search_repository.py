from typing import List, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.paper import Paper as PaperModel


class SearchRepository:
    """Repository for search-related database operations."""

    @staticmethod
    async def search_papers_by_embeddings(
        db: AsyncSession, embeddings: List[List[float]], limit: int = 5, threshold: float = 0.4
    ) -> List[Tuple[PaperModel, float]]:
        """
        Perform a vector search for papers based on a list of embeddings.
        Returns a list of (PaperModel, avg_distance) tuples ordered by ascending distance.
        """

        # Build distance expressions
        distance_exprs = [PaperModel.embedding.cosine_distance(emb) for emb in embeddings]
        total_distance = sum(distance_exprs)
        avg_distance = total_distance / len(embeddings)

        stmt = (
            select(PaperModel, avg_distance.label("avg_distance"))
            .where(avg_distance < threshold)
            .order_by(avg_distance.asc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        rows = result.fetchall()
        return [(paper, float(dist)) for paper, dist in rows]
