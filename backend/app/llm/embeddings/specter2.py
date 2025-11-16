import logging
from typing import List, Optional

import torch
from adapters import AutoAdapterModel
from transformers import AutoTokenizer

logger = logging.getLogger(__name__)


# ---------------------------------------------------
# Reusable text-building utility (official format)
# ---------------------------------------------------
def build_specter2_text(title: str, abstract: str, tokenizer: AutoTokenizer) -> str:
    """Create the official SPECTER2 input: title + [SEP] + abstract."""
    t = title or ""
    a = abstract or ""
    return t + tokenizer.sep_token + a


class Specter2Embedder:
    """Wrapper around the SPECTER2 retrieval (proximity) model."""

    def __init__(self, device: Optional[str] = None) -> None:

        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        self.device = torch.device(device)
        logger.info(f"Loading SPECTER2 base + proximity adapter on {self.device}...")

        # Load tokenizer + base model
        self.tokenizer = AutoTokenizer.from_pretrained(
            "allenai/specter2_base",
            trust_remote_code=True
        )

        self.model = AutoAdapterModel.from_pretrained(
            "allenai/specter2_base",
            trust_remote_code=True
        )

        # Load retrieval adapter (proximity)
        self.model.load_adapter(
            "allenai/specter2",
            load_as="proximity",
            set_active=True,
            source="hf"
        )

        self.model.to(self.device)
        self.model.eval()

        logger.info("SPECTER2 model + adapter loaded successfully.")

    def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Return SPECTER2 embeddings for a batch of prepared input texts."""

        try:
            # Clean newlines only; no other preprocessing
            cleaned = [t.replace("\n", " ") for t in texts]

            inputs = self.tokenizer(
                cleaned,
                padding=True,
                truncation=True,
                return_tensors="pt",
                max_length=512,
                return_token_type_ids=False,
            ).to(self.device)

            with torch.no_grad():
                out = self.model(**inputs)
                cls_vectors = out.last_hidden_state[:, 0, :].cpu().numpy()

            return [v.tolist() for v in cls_vectors]

        except torch.cuda.OutOfMemoryError:
            logger.error("CUDA OOM — reduce batch size.")
            torch.cuda.empty_cache()
            return [None] * len(texts)

        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return [None] * len(texts)

    def embed_one(self, text: str) -> Optional[List[float]]:
        return self.embed_batch([text])[0]
