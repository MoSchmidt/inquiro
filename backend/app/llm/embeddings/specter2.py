import logging
from typing import List, Optional

import torch
from transformers import AutoTokenizer, AutoAdapterModel

logger = logging.getLogger(__name__)


# ---------------------------------------------------
# Reusable text-building utility (official format)
# ---------------------------------------------------
def build_specter2_text(title: str, abstract: str, tokenizer: AutoTokenizer) -> str:
    """Create the official SPECTER2 input format: title + [SEP] + abstract."""
    t = title or ""
    a = abstract or ""
    return t + tokenizer.sep_token + a


class Specter2Embedder:
    """Wrapper around the SPECTER2 retrieval (proximity) model."""

    def __init__(self, device: Optional[str] = None) -> None:
        """Load SPECTER2 tokenizer, base model, and proximity adapter."""
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        self.device = torch.device(device)
        logger.info("Loading SPECTER2 base + proximity adapter on %s...", self.device)

        # Load tokenizer + base model
        self.tokenizer = AutoTokenizer.from_pretrained("allenai/specter2_base")

        self.model = AutoAdapterModel.from_pretrained("allenai/specter2_base")

        # Load retrieval adapter (proximity)
        self.model.load_adapter(
            "allenai/specter2",
            load_as="proximity",
            set_active=True,
            source="hf",
        )

        self.model.to(self.device)
        self.model.eval()

        logger.info("SPECTER2 model + adapter loaded successfully.")

    def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Compute SPECTER2 embeddings for a batch of input texts.
        Returns a list of dense vectors or None for failed items.
        """
        try:
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
                outputs = self.model(**inputs)
                cls_vectors = outputs.last_hidden_state[:, 0, :].cpu().numpy()

            return [v.tolist() for v in cls_vectors]

        except torch.cuda.OutOfMemoryError:
            logger.error("CUDA OOM — reduce batch size.")
            torch.cuda.empty_cache()
            return [None] * len(texts)

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Embedding error: %s", e)
            return [None] * len(texts)

    def embed_one(self, text: str) -> Optional[List[float]]:
        """Compute a single SPECTER2 embedding."""
        return self.embed_batch([text])[0]
