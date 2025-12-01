import logging
import re
from typing import Any, Iterable, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.deps import get_openai_provider, get_specter2_query_embedder
from app.repositories.search_repository import SearchRepository
from app.schemas.search_dto import PaperDto, SearchResponse

logger = logging.getLogger("inquiro")


class SearchService:
    """
    Service for managing search requests.
    """

    MAX_KEYWORD_RETRIES = 2

    @staticmethod
    async def search_papers(query: str, db: AsyncSession) -> SearchResponse:
        """Returns a list of matching papers based on the query."""

        openai_provider = get_openai_provider()

        # Extract + normalize keywords with retry
        keywords = SearchService._extract_keywords_with_retry(
            openai_provider=openai_provider,
            query=query,
            max_retries=SearchService.MAX_KEYWORD_RETRIES,
        )
        logger.info("Keywords: %s", keywords)

        # Generate query embeddings
        embedder = get_specter2_query_embedder()
        embeddings = embedder.embed_batch(keywords)

        rows = await SearchRepository.search_papers_by_embeddings(
            db=db, embeddings=embeddings, limit=5
        )

        results: List[PaperDto] = []

        # Iterate over resolved results
        for doc, avg_dist in rows:
            logger.info("Match: %s... | Avg. Distance: %.4f", doc.title[:30], avg_dist)

            results.append(
                PaperDto(
                    paper_id=doc.paper_id,
                    doi=doc.doi,
                    source=str(doc.source),
                    paper_type=str(doc.paper_type),
                    title=doc.title,
                    authors=doc.authors,
                    abstract=doc.abstract,
                    published_at=doc.published_at,
                )
            )

        logger.info("Found %d papers for query: '%s'", len(results), query)

        return SearchResponse(papers=results)

    @staticmethod
    def _extract_keywords_with_retry(
        openai_provider: Any,
        query: str,
        max_retries: int = 2,
    ) -> List[str]:
        """
        Extract keywords from the provider with retries and format normalization
        Falls back to [query] if all attempts fail or produce no valid keywords
        """
        last_error: Exception | None = None

        for attempt in range(max_retries + 1):
            try:
                raw = openai_provider.extract_keywords(query)
                keywords = SearchService._normalize_keywords(raw)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                # We intentionally catch all Exceptions here. Any failure triggers a fallback.
                last_error = exc
                logger.exception(
                    "Keyword extraction failed on attempt %d/%d",
                    attempt + 1,
                    max_retries + 1,
                )
                keywords = []

            if keywords:
                return keywords

        # All retries failed or produced unusable keywords
        if last_error:
            logger.warning(
                "Keyword extraction failed after %d attempts; "
                "falling back to raw query embedding. Last error: %s",
                max_retries + 1,
                last_error,
            )
        else:
            logger.warning(
                "Keyword extraction returned empty/invalid data after %d attempts; "
                "falling back to raw query embedding.",
                max_retries + 1,
            )

        return [query]

    @staticmethod
    def _normalize_keywords(raw: Any) -> List[str]:
        """
        Normalize various possible responses into a list[str]
        """
        if raw is None:
            return []

        # Already an iterable (list, tuple, set); clean strings and pack into list
        if isinstance(raw, (list, tuple, set)):
            return SearchService._clean_string_list(raw)

        # Single string; try to separate
        if isinstance(raw, str):
            parts = re.split(r"[,;|\n]", raw)
            return SearchService._clean_string_list(parts)

        # Dictionary; try likely keys, else give up
        if isinstance(raw, dict):
            for key in ("keywords", "data", "items", "results"):
                if key in raw:
                    return SearchService._normalize_keywords(raw[key])

            logger.warning(
                "Keyword extraction returned dict with unknown keys: %s", list(raw.keys())
            )
            return []

        # All other formats; give up
        logger.warning(
            "Keyword extraction returned unexpected type %s; converting to string", type(raw)
        )
        return []

    @staticmethod
    def _clean_string_list(items: Iterable[Any]) -> List[str]:
        """
        Takes an iterable of items, converts it to strings, strips whitespace, and drops empties
        """
        cleaned: List[str] = []
        for item in items:
            if item is None:
                continue

            if isinstance(item, str):
                s = item.strip()
            else:
                s = str(item).strip()

            if s:
                cleaned.append(s)

        return cleaned
