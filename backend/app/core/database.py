"""Database configuration and session utilities for the API."""

import logging
from importlib import import_module
from typing import Tuple

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

logger = logging.getLogger("inquiro")

Base = declarative_base()

engine = create_engine(
    settings.DATABASE_URL,
    echo=(settings.ENVIRONMENT == "dev"),
)

SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _timestamp_sql(dialect_name: str) -> Tuple[str, str]:
    """Return dialect-specific SQL fragments for timestamp columns."""

    if dialect_name == "postgresql":
        return "TIMESTAMPTZ", "NOW()"
    if dialect_name == "sqlite":
        return "TIMESTAMP", "CURRENT_TIMESTAMP"
    return "TIMESTAMP", "CURRENT_TIMESTAMP"


def _migrate_legacy_users_table() -> None:
    """Rename and backfill the legacy ``users`` table if it exists."""

    with engine.begin() as connection:
        inspector = inspect(connection)
        existing_tables = set(inspector.get_table_names())
        if "user" in existing_tables or "users" not in existing_tables:
            return

        logger.info("🚚 Migrating legacy users table to new schema...")
        connection.execute(text('ALTER TABLE "users" RENAME TO "user"'))

        inspector = inspect(connection)
        columns = {column["name"] for column in inspector.get_columns("user")}

        if "id" in columns:
            connection.execute(text('ALTER TABLE "user" RENAME COLUMN id TO user_id'))

        if "created_at" not in columns:
            column_type, default_expr = _timestamp_sql(connection.dialect.name)
            connection.execute(
                text(
                    f'ALTER TABLE "user" ADD COLUMN created_at {column_type} DEFAULT {default_expr}'
                )
            )
            connection.execute(
                text(f'UPDATE "user" SET created_at = {default_expr} WHERE created_at IS NULL')
            )

        logger.info("✅ Legacy users table migrated.")


def init_db() -> None:
    """Automatically create or update tables based on SQLAlchemy models."""

    _migrate_legacy_users_table()

    for module in (
            "app.models.user",
            "app.models.project",
            "app.models.paper",
            "app.models.project_paper",
    ):
        import_module(module)
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
