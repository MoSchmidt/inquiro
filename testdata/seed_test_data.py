"""Seed the local development database with test data.

This script populates the database with:
- A test user (username: 'test')
- A test project (name: 'My Test Project')
- Papers from the test-data.parquet file

Usage:
    python testdata/seed_test_data.py
"""

import json
import logging
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any, List, Optional, Tuple

import numpy as np
import pandas as pd
import psycopg2
from psycopg2.extensions import connection
from psycopg2.extras import execute_values

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# Database configuration from environment variables (with local dev defaults)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5433")),
    "user": os.getenv("DB_USER", "inquiro"),
    "password": os.getenv("DB_PASSWORD", "inquiro"),
    "dbname": os.getenv("DB_NAME", "inquiro_db"),
}

TEST_USERNAME = "test"
TEST_PROJECT_NAME = "My Test Project"


def parse_date(d: Optional[str]) -> Optional[date]:
    """Parse YYYY-MM-DD into a date object or return None."""
    if not d:
        return None
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except ValueError:
        return None


def to_plain(x: Any) -> Any:
    """Convert numpy objects recursively to plain Python types."""
    if isinstance(x, np.ndarray):
        return [to_plain(v) for v in x.tolist()]
    if isinstance(x, (list, tuple)):
        return [to_plain(v) for v in x]
    if isinstance(x, dict):
        return {k: to_plain(v) for k, v in x.items()}
    if isinstance(x, np.generic):
        return x.item()
    return x


def authors_to_json(x: Any) -> str:
    """Convert author list structure into JSON string."""
    try:
        return json.dumps(to_plain(x))
    except (TypeError, ValueError):
        return "[]"


def embedding_to_literal(embedding: Any) -> str:
    """Convert embedding array into PostgreSQL vector literal."""
    if hasattr(embedding, "tolist"):
        embedding = embedding.tolist()
    return "[" + ",".join(f"{float(v):.6f}" for v in embedding) + "]"


def build_row(row: Any) -> Optional[Tuple[Any, ...]]:
    """Build a single row tuple for DB insertion."""
    doi = getattr(row, "doi", None)
    if not doi:
        return None
    title: str = (getattr(row, "title", "") or "").strip()
    abstract: str = (getattr(row, "abstract", "") or "").strip()
    published_at = parse_date(getattr(row, "update_date", None))
    raw_authors = getattr(row, "authors_parsed", None)
    authors_json = authors_to_json(raw_authors)
    arxiv_id = getattr(row, "id", None)
    paper_id_external = arxiv_id or None
    embedding = getattr(row, "embedding", None)
    if embedding is None:
        return None
    embedding_literal = embedding_to_literal(embedding)

    return (
        doi,
        "ARXIV",
        "PREPRINT",
        title,
        authors_json,
        abstract,
        published_at,
        paper_id_external,
        embedding_literal,
    )


def insert_papers(conn: connection, rows: List[Tuple[Any, ...]]) -> None:
    """Insert a batch of paper rows into the database."""
    if not rows:
        return

    query = """
        INSERT INTO public.paper (
            doi,
            source,
            paper_type,
            title,
            authors,
            abstract,
            published_at,
            paper_id_external,
            embedding
        )
        VALUES %s
        ON CONFLICT (doi) DO NOTHING
    """

    template = "(" + ",".join(["%s"] * 8) + ", %s::vector)"

    with conn.cursor() as cur:
        execute_values(cur, query, rows, template=template)

    conn.commit()


def create_test_user(conn: connection) -> int:
    """Create the test user and return the user_id."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public."user" (username)
            VALUES (%s)
            ON CONFLICT (username) DO NOTHING
            RETURNING user_id
            """,
            (TEST_USERNAME,),
        )
        result = cur.fetchone()
        if result:
            user_id = result[0]
            logger.info("Created test user '%s' with user_id=%d", TEST_USERNAME, user_id)
        else:
            cur.execute(
                'SELECT user_id FROM public."user" WHERE username = %s',
                (TEST_USERNAME,),
            )
            user_id = cur.fetchone()[0]
            logger.info("Test user '%s' already exists with user_id=%d", TEST_USERNAME, user_id)

    conn.commit()
    return user_id


def create_test_project(conn: connection, user_id: int) -> int:
    """Create the test project and return the project_id."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.project (created_by, project_name)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            RETURNING project_id
            """,
            (user_id, TEST_PROJECT_NAME),
        )
        result = cur.fetchone()
        if result:
            project_id = result[0]
            logger.info("Created test project '%s' with project_id=%d", TEST_PROJECT_NAME, project_id)
        else:
            cur.execute(
                "SELECT project_id FROM public.project WHERE created_by = %s AND project_name = %s",
                (user_id, TEST_PROJECT_NAME),
            )
            row = cur.fetchone()
            if row:
                project_id = row[0]
                logger.info(
                    "Test project '%s' already exists with project_id=%d",
                    TEST_PROJECT_NAME,
                    project_id,
                )
            else:
                cur.execute(
                    """
                    INSERT INTO public.project (created_by, project_name)
                    VALUES (%s, %s)
                    RETURNING project_id
                    """,
                    (user_id, TEST_PROJECT_NAME),
                )
                project_id = cur.fetchone()[0]
                logger.info("Created test project '%s' with project_id=%d", TEST_PROJECT_NAME, project_id)

    conn.commit()
    return project_id


def ingest_papers(conn: connection, parquet_path: Path, batch_size: int = 1000) -> None:
    """Ingest papers from the parquet file into the database."""
    logger.info("Loading papers from %s", parquet_path)

    df: pd.DataFrame = pd.read_parquet(parquet_path)
    logger.info("Found %d papers in parquet file", len(df))

    rows: List[Tuple[Any, ...]] = []
    skipped = 0

    for row in df.itertuples(index=False):
        row_tuple = build_row(row)
        if row_tuple is None:
            skipped += 1
            continue
        rows.append(row_tuple)
        if len(rows) >= batch_size:
            insert_papers(conn, rows)
            logger.info("Inserted batch of %d papers", len(rows))
            rows.clear()

    if rows:
        insert_papers(conn, rows)
        logger.info("Inserted final batch of %d papers", len(rows))

    logger.info("Paper ingestion complete. Skipped %d rows without embeddings.", skipped)


def ensure_doi_index(conn: connection) -> None:
    """Ensure unique index on paper.doi exists."""
    with conn.cursor() as cur:
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_paper_doi ON public.paper(doi);")
    conn.commit()


def main() -> None:
    """Main entrypoint for seeding test data."""
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    parquet_path = script_dir / "test-data.parquet"

    if not parquet_path.exists():
        logger.error("Parquet file not found: %s", parquet_path)
        return

    logger.info("Connecting to database at %s:%s", DB_CONFIG["host"], DB_CONFIG["port"])
    conn = psycopg2.connect(**DB_CONFIG)

    try:
        ensure_doi_index(conn)
        user_id = create_test_user(conn)
        create_test_project(conn, user_id)
        ingest_papers(conn, parquet_path)
        logger.info("Test data seeding complete!")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
