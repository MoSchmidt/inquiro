"""Provides dependency-injected access to shared service instances for the FastAPI app."""

from functools import lru_cache
from typing import Optional

from fastapi import Query

from app.constants.sort_constants import SortDirection
from app.llm.embeddings.specter2 import Specter2Embedder
from app.llm.openai.provider import OpenAIProvider
from app.schemas.generic import SortRequestDto, SearchTextRequestDto


@lru_cache(maxsize=1)
def get_specter2_proximity_embedder() -> Specter2Embedder:
    """Return a shared Specter2Embedder instance, initialized once."""
    return Specter2Embedder()


@lru_cache(maxsize=1)
def get_specter2_query_embedder() -> Specter2Embedder:
    """Return a shared Specter2Embedder instance, initialized once."""
    return Specter2Embedder(model="allenai/specter2_adhoc_query")


@lru_cache(maxsize=1)
def get_openai_provider() -> OpenAIProvider:
    """
    Return a shared OpenAI instance, initialized once.
    """
    return OpenAIProvider()


# ───────────────────────────────────────────────
# Request Dependencies
# ───────────────────────────────────────────────
def get_optional_sort(
        sort_by: Optional[str] = Query(None),
        sort_order: Optional[SortDirection] = Query(None),
) -> Optional[SortRequestDto]:
    """Return SortRequestDto only when at least one sort parameter is provided."""
    if sort_by is None and sort_order is None:
        return None
    return SortRequestDto(sort_by=sort_by, sort_order=sort_order)


def get_optional_search(
        search_text: Optional[str] = Query(None)
) -> Optional[SearchTextRequestDto]:
    """Return SearchTextRequestDto only when search_text is provided."""
    if search_text is None:
        return None
    return SearchTextRequestDto(search_text=search_text)
