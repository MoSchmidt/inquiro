import json
from pathlib import Path
from typing import Dict, List

import torch
from transformers import AutoModel, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("allenai/specter2_base", trust_remote_code=True)
model = AutoModel.from_pretrained("allenai/specter2_base", trust_remote_code=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)


def embed_text(text: str) -> List[float]:
    # tokenizer.sep_token = "[SEP]"
    text = text.replace("\n", " ")
    inputs = tokenizer(
        text,
        padding=True,
        truncation=True,
        return_tensors="pt",
        return_token_type_ids=False,
        max_length=512,
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)

    # CLS embedding
    emb = outputs.last_hidden_state[:, 0, :].squeeze().cpu().numpy()
    return emb.tolist()


def ingest_arxiv_metadata(json_path: str, limit: int = 50) -> List[Dict]:
    """
    Reads the arXiv metadata snapshot JSONL file and processes
    the first `limit` papers.

    Returns a list of dicts:
    [
        {
            "id": "...",
            "title": "...",
            "abstract": "...",
            "categories": "...",
            "embedding": [...]
        },
        ...
    ]
    """
    json_path = Path(json_path)
    if not json_path.exists():
        raise FileNotFoundError(f"Could not find dataset at {json_path}")

    papers: List[Dict] = []

    with json_path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= limit:
                break

            data = json.loads(line)

            title = data.get("title", "").strip()
            abstract = data.get("abstract", "").strip()
            categories = data.get("categories", "")

            full_text = f"{title}. {abstract}"

            # Generate embedding
            vector = embed_text(full_text)

            papers.append(
                {
                    "id": data.get("id"),
                    "title": title,
                    "abstract": abstract,
                    "categories": categories,
                    "embedding": vector,
                }
            )

    print(f"Processed {len(papers)} papers.")
    return papers


# local testing only!
if __name__ == "__main__":
    # ⚠️ change this to your real path
    json_path = r"C:\arxiv-metadata-oai-snapshot.json"

    papers = ingest_arxiv_metadata(
        json_path=json_path,
        limit=5,
    )

    for p in papers:
        print(p["id"], p["title"][:80])
