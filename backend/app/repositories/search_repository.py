from datetime import date
from typing import List, Optional, Tuple, Union

from sqlalchemy import ColumnElement, and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.paper import Paper as PaperModel
from app.schemas.search_dto import (
    AdvancedSearchFilter,
    ConditionGroup,
    TextCondition,
)

# Mapping from DTO field names to SQLAlchemy model columns
_FIELD_COLUMN = {
    "title": PaperModel.title,
    "abstract": PaperModel.abstract,
}


class SearchRepository:
    """Repository for search-related database operations."""

    @staticmethod
    async def search_papers_by_embeddings(
        db: AsyncSession,
        embeddings: List[List[float]],
        limit: int = 5,
        threshold: float = 0.4,
        search_filter: Optional[AdvancedSearchFilter] = None,
    ) -> List[Tuple[PaperModel, float]]:
        """
        Perform a vector search for papers based on a list of embeddings.
        Returns a list of (PaperModel, avg_distance) tuples ordered by ascending distance.
        Optionally applies advanced search filters (year range, text conditions).
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

        if search_filter:
            clauses = SearchRepository._build_filter_clauses(search_filter)
            if clauses:
                stmt = stmt.where(and_(*clauses))

        result = await db.execute(stmt)
        rows = result.fetchall()
        return [(paper, float(dist)) for paper, dist in rows]

    @staticmethod
    def _build_filter_clauses(search_filter: AdvancedSearchFilter) -> list:
        """Build a list of top-level SQLAlchemy filter clauses from the advanced filter."""
        clauses = []

        if search_filter.year_from is not None:
            clauses.append(PaperModel.published_at >= date(search_filter.year_from, 1, 1))

        if search_filter.year_to is not None:
            clauses.append(PaperModel.published_at <= date(search_filter.year_to, 12, 31))

        condition_clause = SearchRepository._build_group_clause(search_filter.root)
        if condition_clause is not None:
            clauses.append(condition_clause)

        return clauses

    @staticmethod
    def _build_group_clause(group: ConditionGroup) -> Optional[ColumnElement[bool]]:
        """Recursively build an AND/OR clause from a ConditionGroup."""
        if not group.children:
            return None

        child_clauses = []
        for child in group.children:
            clause = SearchRepository._build_node_clause(child)
            if clause is not None:
                child_clauses.append(clause)

        if not child_clauses:
            return None

        if group.operator == "AND":
            return and_(*child_clauses)
        return or_(*child_clauses)

    @staticmethod
    def _build_node_clause(
        node: Union[TextCondition, ConditionGroup],
    ) -> Optional[ColumnElement[bool]]:
        """Build a clause for a single node (condition or nested group)."""
        if node.type == "group":
            return SearchRepository._build_group_clause(node)

        column = _FIELD_COLUMN[node.field]
        pattern = f"%{node.value}%"

        if node.operator == "contains":
            return column.ilike(pattern)
        return or_(column.is_(None), ~column.ilike(pattern))
