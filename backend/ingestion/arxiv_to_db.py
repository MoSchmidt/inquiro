import argparse
import json
import logging
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
import psycopg2
from psycopg2.extensions import connection
from psycopg2.extras import execute_values

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

DB_CONFIG: dict[str, Any] = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": int(os.getenv("POSTGRES_PORT") or 5432),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "dbname": os.getenv("POSTGRES_DB"),
    "sslmode": "require",
}

TABLE = "paper"


def iter_shards(data_dir: Path) -> Iterable[Path]:
    """Return all parquet shard paths in sorted order."""
    return sorted(data_dir.glob("shard_*.parquet"))


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


def ensure_doi_index(conn: connection) -> None:
    """Ensure unique index on paper.doi exists."""
    with conn.cursor() as cur:
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_paper_doi ON public.paper(doi);")
    conn.commit()


def embedding_to_literal(embedding: Any) -> str:
    """Convert embedding array into PostgreSQL vector literal."""
    if hasattr(embedding, "tolist"):
        embedding = embedding.tolist()
    return "[" + ",".join(f"{float(v):.6f}" for v in embedding) + "]"


def insert_rows(conn: connection, rows: List[Tuple[Any, ...]]) -> None:
    """Insert a batch of rows into the paper table."""
    if not rows:
        return

    query = f"""
        INSERT INTO public.{TABLE} (
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


def build_row(row: Any) -> Optional[Tuple[Any, ...]]:
    """Build a single row tuple for DB insertion."""
    doi = getattr(row, "doi", None)
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


def ingest_shard(conn: connection, shard_path: Path, batch_size: int) -> None:
    """Ingest a single parquet shard into the database."""
    logger.info("Ingesting %s", shard_path.name)

    df: pd.DataFrame = pd.read_parquet(shard_path)
    rows: List[Tuple[Any, ...]] = []

    for row in df.itertuples(index=False):
        row_tuple = build_row(row)
        if row_tuple is None:
            continue
        rows.append(row_tuple)
        if len(rows) >= batch_size:
            insert_rows(conn, rows)
            rows.clear()


def main(data_dir: Path, batch_size: int) -> None:
    """Main entrypoint for bulk ingestion."""
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        ensure_doi_index(conn)
        for shard in iter_shards(data_dir):
            ingest_shard(conn, shard, batch_size=batch_size)
    finally:
        conn.close()


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_data_path = os.path.join(script_dir, "arxiv-vector-embeddings")

    parser = argparse.ArgumentParser(description="Bulk ingest arXiv parquet shards.")
    parser.add_argument("--data-dir", type=str, default=default_data_path)
    parser.add_argument("--batch-size", type=int, default=1000)
    args = parser.parse_args()

    main(Path(args.data_dir), args.batch_size)
