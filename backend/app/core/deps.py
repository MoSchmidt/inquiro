"""Provides dependency-injected access to shared service instances for the FastAPI app."""

from app.llm.embeddings.specter2 import Specter2Embedder

_embedder: Specter2Embedder | None = None

def get_specter2_embedder() -> Specter2Embedder:
    """Return a shared Specter2Embedder instance, initializing it on first use."""
    global _embedder
    if _embedder is None:
        _embedder = Specter2Embedder()
    return _embedder
