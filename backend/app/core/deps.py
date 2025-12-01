"""Provides dependency-injected access to shared service instances for the FastAPI app."""

from functools import lru_cache

from app.llm.embeddings.specter2 import Specter2Embedder
from app.llm.openai.provider import OpenAIProvider


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
