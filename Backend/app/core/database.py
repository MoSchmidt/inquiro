import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

logger = logging.getLogger("inquiro")

Base = declarative_base()

engine = create_engine(
    settings.DATABASE_URL,
    echo=(settings.ENVIRONMENT == "dev"),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Automatically create or update tables based on models."""
    import app.models  # noqa: F401 (ensures models are imported)
    logger.info("🔄 Creating / updating database schema...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database schema up to date.")


def get_db():
    """Provide a database session for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
