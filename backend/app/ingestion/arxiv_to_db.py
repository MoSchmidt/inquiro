import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

DB_CONFIG = {
    "host": "inquiro-db.cxa6mocs0pr2.eu-central-1.rds.amazonaws.com",
    "port": 5432,
    "user": "postgres",
    "password": "inquiroDB#0815",
    "dbname": "inquiro_db",
}

TABLE_NAME = "paper"


def iter_shards(data_dir: Path) -> Iterable[Path]:
    """Yield all shard_XXXXX.parquet files in sorted order."""
    return sorted(data_dir.glob("shard_*.parquet"))


def parse_date(date_str: Optional[str]):
    """Parse YYYY-MM-DD or return None."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def embedding_to_vector_literal(embedding: List[float]) -> str:
    """Convert list[float] to pgvector literal like [0.1,0.2,...]."""
    return "[" + ",".join(f"{x:.6f}" for x in embedding) + "]"


def to_plain(obj):
    """Recursively convert numpy arrays/types into plain Python types."""
    if isinstance(obj, np.ndarray):
        return [to_plain(x) for x in obj.tolist()]
    if isinstance(obj, (np.float32, np.float64, np.int32, np.int64)):
        return obj.item()
    if isinstance(obj, list):
        return [to_plain(x) for x in obj]
    if isinstance(obj, dict):
        return {k: to_plain(v) for k, v in obj.items()}
    return obj


def ingest_shard(conn, shard_path: Path, batch_size: int = 500) -> None:
    """Read a single parquet shard and insert its rows into the DB."""
    logger.info("Ingesting %s", shard_path.name)
    df = pd.read_parquet(shard_path)

    # Columns from your shard inspection
    id_col = "id"
    title_col = "title"
    abstract_col = "abstract"
    doi_col = "doi"
    authors_parsed_col = "authors_parsed"
    update_date_col = "update_date"
    embedding_col = "embedding"

    rows: List[Tuple] = []

    for _, row in df.iterrows():
        arxiv_id = row.get(id_col)

        title = (row.get(title_col) or "").strip()
        abstract = (row.get(abstract_col) or "").strip()
        doi = row.get(doi_col) or None

        update_date = row.get(update_date_col)
        published_at = parse_date(update_date)

        raw_authors = row.get(authors_parsed_col)
        if raw_authors is None or (isinstance(raw_authors, float) and pd.isna(raw_authors)):
            authors_parsed = []
        else:
            authors_parsed = to_plain(raw_authors)
        authors_json = json.dumps(authors_parsed)

        if arxiv_id:
            url = f"https://arxiv.org/abs/{arxiv_id}"
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        else:
            url = None
            pdf_url = None

        embedding = row[embedding_col]
        if hasattr(embedding, "tolist"):
            embedding = embedding.tolist()
        embedding_literal = embedding_to_vector_literal(embedding)

        source = "ARXIV"
        paper_type = "PREPRINT"

        rows.append(
            (
                doi,
                source,
                paper_type,
                title,
                authors_json,
                abstract,
                published_at,
                pdf_url,
                url,
                embedding_literal,
            )
        )

        if len(rows) >= batch_size:
            insert_rows(conn, rows)
            rows.clear()

    if rows:
        insert_rows(conn, rows)


def insert_rows(conn, rows: List[Tuple]) -> None:
    """Insert a batch into public.paper (paper_id auto-generated)."""
    with conn.cursor() as cur:
        query = f"""
            INSERT INTO public.{TABLE_NAME} (
                doi,
                source,
                paper_type,
                title,
                authors,
                abstract,
                published_at,
                pdf_url,
                url,
                embedding
            )
            VALUES %s
        """
        # Last value is a string like "[0.1,0.2,...]" → cast to vector
        template = "(" + ",".join(["%s"] * 9) + ", %s::vector)"
        execute_values(cur, query, rows, template=template)

    conn.commit()


def main(data_dir: Path, batch_size: int) -> None:
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        for shard in iter_shards(data_dir):
            ingest_shard(conn, shard, batch_size=batch_size)
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Load ArXiv parquet shards with embeddings into the paper table."
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        required=True,
        help="Directory containing shard_XXXXX.parquet files",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Number of rows per DB batch insert",
    )
    args = parser.parse_args()

    main(Path(args.data_dir), args.batch_size)
