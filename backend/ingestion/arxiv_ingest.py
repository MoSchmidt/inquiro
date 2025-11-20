import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from app.llm.embeddings.specter2 import (
    Specter2Embedder,
    build_specter2_text,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def write_shard(shard_buffer: List[Dict], shard_idx: int, out_path: Path) -> int:
    """Write a Parquet shard to disk and return the next shard index."""
    df = pd.DataFrame(shard_buffer)
    shard_file = out_path / f"shard_{shard_idx:05d}.parquet"
    df.to_parquet(shard_file, index=False)
    logger.info("✔ Wrote shard %s → %s (%s rows)", shard_idx, shard_file, len(df))
    return shard_idx + 1


def process_batch(batch_buffer: List[Dict], embedder: Specter2Embedder) -> List[Dict]:
    """Convert a batch of metadata dicts into embedding rows."""
    texts = [
        build_specter2_text(
            p.get("title", ""),
            p.get("abstract", ""),
            embedder.tokenizer,
        )
        for p in batch_buffer
    ]

    vectors = embedder.embed_batch(texts)

    rows: List[Dict] = []
    for original, vec in zip(batch_buffer, vectors):
        if vec is None:
            continue

        row = dict(original)
        row["embedding"] = vec
        rows.append(row)

    return rows


# pylint: disable=too-many-arguments, too-many-positional-arguments, too-many-locals
def ingest_arxiv_metadata_to_parquet(
    path: str,
    out_dir: str,
    embedder: Specter2Embedder,
    limit: Optional[int] = None,
    batch_size: int = 64,
    shard_size: int = 5000,
) -> None:
    """Ingest a JSONL ArXiv dump and write Parquet shards with embeddings."""
    json_file = Path(path)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    if not json_file.exists():
        raise FileNotFoundError(f"Dataset not found: {json_file}")

    logger.info("Reading: %s", json_file)
    logger.info("Writing shards: %s", out_path)

    batch_buffer: List[Dict] = []
    shard_buffer: List[Dict] = []
    shard_idx = 0

    with json_file.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if limit and i >= limit:
                break

            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                logger.warning("Skipping invalid JSON at line %s", i)
                continue

            batch_buffer.append(data)

            if len(batch_buffer) == batch_size:
                rows = process_batch(batch_buffer, embedder)
                shard_buffer.extend(rows)
                batch_buffer.clear()

                if len(shard_buffer) >= shard_size:
                    shard_idx = write_shard(shard_buffer, shard_idx, out_path)
                    shard_buffer.clear()

            if (i + 1) % 1000 == 0:
                logger.info("Processed %s papers...", i + 1)

    if batch_buffer:
        rows = process_batch(batch_buffer, embedder)
        shard_buffer.extend(rows)

    if shard_buffer:
        write_shard(shard_buffer, shard_idx, out_path)

    logger.info("Done. Total shards: %s", shard_idx + 1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest ArXiv metadata into Parquet shards.")
    parser.add_argument("--path", type=str, required=True)
    parser.add_argument("--out", type=str, required=True)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--shard-size", type=int, default=5000)
    parser.add_argument("--device", type=str, default=None)

    args = parser.parse_args()

    cli_embedder = Specter2Embedder(device=args.device)

    ingest_arxiv_metadata_to_parquet(
        path=args.path,
        out_dir=args.out,
        embedder=cli_embedder,
        limit=args.limit,
        batch_size=args.batch_size,
        shard_size=args.shard_size,
    )
