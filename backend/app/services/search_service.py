import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_openai_provider, get_specter2_query_embedder
from app.models.paper import Paper as PaperModel
from app.schemas.search_dto import Paper, SearchResponse

logger = logging.getLogger("inquiro")


class SearchService:
    """
    Service for managing search requests
    """

    @staticmethod
    def search_papers(query: str, db: Session) -> SearchResponse:
        """
        Returns a list of matching papers based on the query
        """
        openai_provider = get_openai_provider()
        keywords = openai_provider.extract_keywords(query)
        logger.info("Keywords: %s", keywords)

        # Fallback if keyword extraction returns an empty list
        if not keywords:
            logger.warning("No keywords extracted; falling back to raw query embedding.")
            keywords = [query]

        embedder = get_specter2_query_embedder()
        embeddings = embedder.embed_batch(keywords)

        # Perform vector search to find matching papers in DB
        distance_exprs = [PaperModel.embedding.cosine_distance(emb) for emb in embeddings]
        total_distance = sum(distance_exprs)
        avg_distance = total_distance / len(embeddings)

        stmt = (
            select(PaperModel, avg_distance.label("avg_distance"))
            .order_by(avg_distance.asc())
            .limit(5)
        )

        rows = db.execute(stmt).all()
        results = []

        for doc, avg_dist in rows:
            logger.info("Match: %s... | Avg. Distance: %.4f", doc.title[:30], avg_dist)

            paper = Paper(
                paper_id=doc.paper_id,
                doi=doc.doi,
                source=doc.source,
                paper_type=doc.paper_type,
                title=doc.title,
                authors=doc.authors,
                abstract=doc.abstract,
                published_at=doc.published_at,
                fetched_at=doc.fetched_at,
            )
            results.append(paper)

        logger.info("Found %d papers for query: '%s'", len(results), query)

        return SearchResponse(papers=results)
