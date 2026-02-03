"""Database configuration and session utilities for the API."""

import logging
from importlib import import_module
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

logger = logging.getLogger("inquiro")

Base = declarative_base()

# Use async engine with asyncpg or aiomysql driver
# Set probes for the vector index for every connection
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=(settings.ENVIRONMENT == "dev"),
    future=True,
    connect_args={"server_settings": {"ivfflat.probes": "50"}},
)

async_session_local = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Automatically create or update tables based on SQLAlchemy models."""
    for module in (
        "app.models.user",
        "app.models.project",
        "app.models.paper",
        "app.models.project_paper",
        "app.models.paper_content",
    ):
        import_module(module)

    logger.info("🔄 Creating / updating database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database schema up to date.")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session for FastAPI routes."""
    async with async_session_local() as session:
        yield session
