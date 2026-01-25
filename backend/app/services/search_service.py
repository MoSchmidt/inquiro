import logging
import re
from typing import Any, Iterable, List, Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_openai_provider, get_specter2_query_embedder
from app.repositories.search_repository import SearchRepository
from app.schemas.search_dto import PaperDto, SearchResponse
from app.utils.author_utils import normalize_authors
from app.utils.pdf_utils import pdf_bytes_to_text
from app.utils.token_utils import ensure_fits_token_limit

logger = logging.getLogger("inquiro")


class SearchService:
    """
    Service for managing search requests.
    """

    MAX_KEYWORD_RETRIES = 2
    MAX_PDF_KEYWORD_INPUT_TOKENS = 280_000

    @staticmethod
    async def search_papers(query: str, db: AsyncSession) -> SearchResponse:
        """
        Search using a free-text query
        """
        openai_provider = get_openai_provider()

        # Extract + normalize keywords with retry
        keywords = await SearchService._extract_keywords_with_retry(
            openai_provider=openai_provider,
            query=query,
            max_retries=SearchService.MAX_KEYWORD_RETRIES,
        )
        logger.info("Text search keywords: %s", keywords)

        return await SearchService._search_with_keywords(
            keywords=keywords,
            db=db,
            user_query=query,
        )

    @staticmethod
    async def search_papers_from_pdf(
            pdf_file: UploadFile,
            db: AsyncSession,
            query: Optional[str] = None,
    ) -> SearchResponse:
        """
        Search using a PDF as the primary signal.
        1. Extract text from PDF.
        2. Optionally combine with user query.
        3. Let the LLM derive search keywords from this context.
        4. Use keywords for vector search.
        """
        content = await pdf_file.read()
        if not content:
            logger.warning("Empty PDF uploaded for search")
            return SearchResponse(papers=[])

        try:
            pdf_text = pdf_bytes_to_text(content)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            filename = pdf_file.filename or "<unknown>"
            logger.warning(
                "Invalid or corrupted PDF uploaded for search: %s; error: %s",
                filename,
                exc,
            )
            # Return a client error instead of 500
            raise HTTPException(
                status_code=400,
                detail="Invalid or corrupted PDF file.",
            ) from exc

        ensure_fits_token_limit(
            pdf_text,
            max_tokens=SearchService.MAX_PDF_KEYWORD_INPUT_TOKENS,
            error_status=413,
            error_detail=(
                "PDF is too large to be used directly for semantic search. "
                "Please try a shorter document or a cropped version."
            ),
        )

        openai_provider = get_openai_provider()
        keywords = await SearchService._extract_pdf_keywords_with_retry(
            openai_provider=openai_provider,
            pdf_text=pdf_text,
            query=query,
            max_retries=SearchService.MAX_KEYWORD_RETRIES,
        )
        logger.info("PDF search keywords: %s", keywords)

        label = query or pdf_file.filename or "pdf-search"
        return await SearchService._search_with_keywords(keywords=keywords, db=db, user_query=label)

    # ---------- Shared search pipeline ----------

    @staticmethod
    async def _search_with_keywords(
            keywords: List[str],
            db: AsyncSession,
            user_query: str,
    ) -> SearchResponse:
        """
        Core embedding + vector-search + DTO mapping pipeline.
        """
        if not keywords:
            logger.warning("No keywords provided for query '%s'", user_query)
            return SearchResponse(papers=[])

        # Generate query embeddings
        embedder = get_specter2_query_embedder()
        embeddings = embedder.embed_batch(keywords)

        rows = await SearchRepository.search_papers_by_embeddings(
            db=db,
            embeddings=embeddings,
            limit=10,
        )

        results: List[PaperDto] = []
        # Iterate over resolved results
        for doc, avg_dist in rows:
            logger.info("Match: %s... | Avg. Distance: %.4f", doc.title[:30], avg_dist)
            authors_value = normalize_authors(doc.authors)
            results.append(
                PaperDto(
                    paper_id=doc.paper_id,
                    doi=doc.doi,
                    source=str(doc.source),
                    paper_type=str(doc.paper_type),
                    title=doc.title,
                    authors=authors_value,
                    abstract=doc.abstract,
                    published_at=doc.published_at,
                )
            )

        logger.info(
            "Found %d papers for query: '%s'",
            len(results),
            user_query,
        )
        return SearchResponse(papers=results)

    # ---------- Helper functions ----------

    @staticmethod
    async def _extract_keywords_with_retry(
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
                raw = await openai_provider.extract_keywords(query)
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
    async def _extract_pdf_keywords_with_retry(
            openai_provider: Any,
            pdf_text: str,
            query: Optional[str],
            max_retries: int = 2,
    ) -> List[str]:
        """
        Extract keywords from PDF text and optional user query with retries.
        """
        last_error: Exception | None = None

        for attempt in range(max_retries + 1):
            try:
                raw = await openai_provider.extract_keywords_from_pdf(
                    pdf_text=pdf_text,
                    query=query,
                )
                keywords = SearchService._normalize_keywords(raw)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                last_error = exc
                logger.exception(
                    "PDF keyword extraction failed on attempt %d/%d", attempt + 1, max_retries + 1
                )
                keywords = []

            if keywords:
                return keywords

        if last_error:
            logger.warning(
                "PDF keyword extraction failed after %d attempts. Last error: %s",
                max_retries + 1,
                last_error,
            )
        else:
            logger.warning(
                "PDF keyword extraction returned empty/invalid data after %d attempts.",
                max_retries + 1,
            )

        return []

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
