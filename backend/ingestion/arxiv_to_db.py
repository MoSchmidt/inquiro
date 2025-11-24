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

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

DB_CONFIG = {
    "host": "inquiro-db.cxa6mocs0pr2.eu-central-1.rds.amazonaws.com",
    "port": 5432,
    "user": "postgres",
    "password": "TODO",
    "dbname": "inquiro_db",
    "sslmode": "require",
}

TABLE = "paper"


def iter_shards(data_dir: Path) -> Iterable[Path]:
    return sorted(data_dir.glob("shard_*.parquet"))


def parse_date(d: Optional[str]):
    if not d:
        return None
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except Exception:
        return None


def to_plain(x):
    if isinstance(x, np.ndarray):
        return [to_plain(v) for v in x.tolist()]
    if isinstance(x, (list, tuple)):
        return [to_plain(v) for v in x]
    if isinstance(x, dict):
        return {k: to_plain(v) for k, v in x.items()}
    if isinstance(x, (np.generic,)):
        return x.item()
    return x


def authors_to_json(x):
    try:
        return json.dumps(to_plain(x))
    except Exception:
        return "[]"


def ensure_doi_index(conn):
    with conn.cursor() as cur:
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_paper_doi ON public.paper(doi);")
    conn.commit()


def embedding_to_literal(embedding):
    if hasattr(embedding, "tolist"):
        embedding = embedding.tolist()
    return "[" + ",".join(f"{float(v):.6f}" for v in embedding) + "]"


def insert_rows(conn, rows: List[Tuple]):
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


def ingest_shard(conn, shard_path: Path, batch_size: int):
    logger.info("Ingesting %s", shard_path.name)
    df = pd.read_parquet(shard_path)

    rows: List[Tuple] = []
    for row in df.itertuples(index=False):
        doi = getattr(row, "doi", None)  # Keep DOI even if None
        title = (getattr(row, "title", "") or "").strip()
        abstract = (getattr(row, "abstract", "") or "").strip()
        published_at = parse_date(getattr(row, "update_date", None))
        raw_authors = getattr(row, "authors_parsed", None)
        authors_json = authors_to_json(raw_authors)
        arxiv_id = getattr(row, "id", None)
        paper_id_external = arxiv_id or None
        embedding = getattr(row, "embedding", None)
        if embedding is None:
            continue
        embedding_literal = embedding_to_literal(embedding)

        rows.append(
            (
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
        )

        if len(rows) >= batch_size:
            insert_rows(conn, rows)
            rows.clear()

    if rows:
        insert_rows(conn, rows)


def main(data_dir: Path, batch_size: int):
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        ensure_doi_index(conn)
        for shard in iter_shards(data_dir):
            ingest_shard(conn, shard, batch_size=batch_size)
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Bulk ingest arXiv parquet shards into paper table."
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=r"C:/Users/AnthonyMalRivett/Documents/arxiv-vector-embeddings",
    )
    parser.add_argument("--batch-size", type=int, default=1000)
    args = parser.parse_args()
    main(Path(args.data_dir), args.batch_size)
