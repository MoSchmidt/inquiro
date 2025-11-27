from typing import List, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.paper import Paper as PaperModel


class SearchRepository:
    """Repository for search-related database operations."""

    @staticmethod
    def search_papers_by_embeddings(
        db: Session, embeddings: List[List[float]], limit: int = 5
    ) -> List[Tuple[PaperModel, float]]:
        """
        Perform a vector search for papers based on a list of embeddings.
        Returns a list of (PaperModel, avg_distance) tuples ordered by ascending distance.
        """
        # Build distance expression for each embedding
        distance_exprs = [PaperModel.embedding.cosine_distance(emb) for emb in embeddings]
        total_distance = sum(distance_exprs)
        avg_distance = total_distance / len(embeddings)

        stmt = (
            select(PaperModel, avg_distance.label("avg_distance"))
            .order_by(avg_distance.asc())
            .limit(limit)
        )

        rows = db.execute(stmt).all()
        return [(paper, float(avg_dist)) for paper, avg_dist in rows]
