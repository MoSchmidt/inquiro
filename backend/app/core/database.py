"""Database configuration and session utilities for the API."""

import logging
from importlib import import_module

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

logger = logging.getLogger("inquiro")

Base = declarative_base()

engine = create_engine(
    settings.DATABASE_URL,
    echo=(settings.ENVIRONMENT == "dev"),
)

SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Automatically create or update tables based on SQLAlchemy models."""
    import_module("app.models.user")
    logger.info("🔄 Creating / updating database schema...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database schema up to date.")


def get_db():
    """Yield a database session for FastAPI routes."""
    db = SESSION_LOCAL()
    try:
        yield db
    finally:
        db.close()
