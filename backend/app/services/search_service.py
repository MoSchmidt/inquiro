from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.paper import Paper as PaperModel
from app.schemas.search_dto import Paper as PaperSchema, SearchResponse
from app.utils.author_utils import normalize_authors

# from app.core.deps import get_openai_provider, get_specter2_query_embedder


class SearchService:
    """
    Service for managing search requests.

    NOTE:
    -----
    For now, we just return the 5 most recently fetched papers from the
    database (ordered by `fetched_at DESC`) to establish the connection
    between the API and the frontend.

    To restore or extend the original behavior that uses OpenAI + SPECTER2
    embeddings, uncomment and adapt the code in `search_papers` below.
    """

    @staticmethod
    def search_papers(db: Session, _query: str) -> SearchResponse:
        """
        Return the 5 most recent papers from the database.

        The `query` parameter is currently ignored; it's kept for future
        use when more advanced search logic is implemented.
        """

        # --- Original implementation (kept for easy reactivation) ---
        # openai_provider = get_openai_provider()
        # keywords = openai_provider.extract_keywords(query)
        #
        # embedder = get_specter2_query_embedder()
        # embeddings = embedder.embed_batch(keywords)
        #
        # # Additionally embed the original query -> could also be used for searching
        # embeddings.append(embedder.embed_one(query))
        #
        # In a future iteration, the embeddings can be used to perform a vector
        # similarity search against the `paper.embedding` column (pgvector) and
        # return semantically relevant results.

        # Simple placeholder: return the 5 most recently fetched papers
        papers_db = (
            db.query(PaperModel)
            .order_by(desc(PaperModel.fetched_at))
            .limit(10)  # fetch a few more and filter below
            .all()
        )

        # Manually map ORM objects to schema to handle slight type/field
        # differences (e.g. authors JSON shape, missing URLs, nullable DOIs).
        paper_schemas: list[PaperSchema] = []
        for p in papers_db:
            # Only require a title; DOI and URLs may be missing or unreliable.
            if not p.title:
                continue

            authors_value = normalize_authors(p.authors)

            paper_schemas.append(
                PaperSchema(
                    paper_id=p.paper_id,
                    doi=p.doi,
                    source=str(getattr(p.source, "value", p.source)),
                    paper_type=str(getattr(p.paper_type, "value", p.paper_type)),
                    title=p.title,
                    authors=authors_value,
                    abstract=p.abstract,
                    published_at=p.published_at,
                    pdf_url=None,
                    url=None,
                    fetched_at=p.fetched_at,
                )
            )

            if len(paper_schemas) >= 5:
                break

        return SearchResponse(papers=paper_schemas)
