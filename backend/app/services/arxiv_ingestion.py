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
    """Generate a SPECTER2 embedding for a text string."""
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

    emb = outputs.last_hidden_state[:, 0, :].squeeze().cpu().numpy()
    return emb.tolist()


def ingest_arxiv_metadata(path: str, limit: int = 50) -> List[Dict]:
    """
    Read the arXiv metadata snapshot JSONL file and process the first `limit` papers.
    """
    json_file = Path(path)

    if not json_file.exists():
        raise FileNotFoundError(f"Could not find dataset at {json_file}")

    papers: List[Dict] = []

    with json_file.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= limit:
                break

            data = json.loads(line)

            title = data.get("title", "").strip()
            abstract = data.get("abstract", "").strip()
            categories = data.get("categories", "")

            full_text = f"{title}. {abstract}"
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


# Local testing only
if __name__ == "__main__":
    test_path = r"C:\arxiv-metadata-oai-snapshot.json"

    test_papers = ingest_arxiv_metadata(
        path=test_path,
        limit=5,
    )

    for p in test_papers:
        print(p["id"], p["title"][:80])
