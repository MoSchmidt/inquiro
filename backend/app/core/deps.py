"""Provides dependency-injected access to shared service instances for the FastAPI app."""
from functools import lru_cache

from app.llm.embeddings.specter2 import Specter2Embedder


@lru_cache(maxsize=1)
def get_specter2_embedder() -> Specter2Embedder:
    """Return a shared Specter2Embedder instance, initialized once."""
    return Specter2Embedder()
