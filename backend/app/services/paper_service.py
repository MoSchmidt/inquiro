import logging
import uuid
from pathlib import Path
from typing import Optional

import httpx
from fastapi import HTTPException
from pypdf import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.database_constants import PaperSource
from app.core.deps import get_openai_provider
from app.llm.token_utils import count_tokens
from app.repositories.paper_repository import PaperRepository
from app.schemas.paper_dto import PaperSummaryResponse

BASE_DIR = Path(__file__).parent.parent
TMP_DIR = BASE_DIR / "tmp"
TMP_DIR.mkdir(exist_ok=True)

# GPT 5 nano has a max. content size of 400k tokens, combining input and output.
# This represents a conservative estimate, leaving enough space for the prompt and output.
MAX_INPUT_TOKENS = 280_000

logger = logging.getLogger("inquiro")


class PaperService:
    """
    Service for summarising research papers
    """

    @staticmethod
    async def summarise_paper(
        paper_id: int, query: str, session: AsyncSession
    ) -> PaperSummaryResponse:
        """
        Retrieves paper specified by id, retrieves its pdf version, and summarises it.
        Returns a summary of the specified paper
        """
        paper = await PaperRepository.get_paper_by_id(session, paper_id)

        if not paper:
            logger.warning("Failed to find specified paper in DB: %s", paper_id)
            raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")

        external_id = paper.paper_id_external
        paper_source = paper.source

        # At the moment we only support arXiv as source; if we intend to add papers from different
        # sources, the necessary functions need to be implemented. Until then just return an
        # exception for unsupported sources.
        if paper_source != PaperSource.ARXIV:
            logger.warning("Unsupported paper source for summarization: %s", paper.source)
            raise HTTPException(
                status_code=422,
                detail=f"Unsupported paper source '{paper_source}'. Only ARXIV is supported.",
            )

        pdf_file: Optional[Path] = None

        try:
            pdf_file = await PaperService._fetch_arxiv_pdf(arxiv_id=external_id)

            pdf_text = PaperService._pdf_to_text(pdf_file)

            # If the pdf is of excessive length (> few hundred pages) it is too big for a single
            # request. We could process the paper in multiple parts but that would be a lot of
            # effort for a tiny proportion of all papers.
            token_count = count_tokens(pdf_text)
            if token_count > MAX_INPUT_TOKENS:
                logger.warning(
                    "Paper %s too large to summarise (estimated tokens: %s)",
                    external_id,
                    token_count,
                )
                raise HTTPException(
                    status_code=413,
                    detail="Paper is too long to be summarised at the moment."
                    "Please try a shorter document.",
                )

            openai_provider = get_openai_provider()
            summary = await openai_provider.summarise_paper(pdf_text, query)
            return PaperSummaryResponse(summary=summary)
        except httpx.HTTPStatusError as exc:
            # arXiv returned 404 or similar error
            logger.warning("Failed to fetch arXiv paper %s: %s", external_id, exc, exc_info=True)
            raise HTTPException(status_code=404, detail="Paper not found")
        except httpx.RequestError as exc:
            logger.warning(
                "Network error while fetching arXiv paper %s: %s", external_id, exc, exc_info=True
            )
            raise HTTPException(
                status_code=503,
                detail="Upstream arXiv service unavailable, please try again later.",
            )
        except Exception:
            # Catch-all for unexpected issues (PDF parsing, LLM errors, ...)
            logger.exception("Error summarising arxiv paper %s", external_id)
            raise HTTPException(
                status_code=500, detail="An unexpected error occurred while summarising the paper."
            )
        finally:
            if pdf_file and pdf_file.exists():
                try:
                    pdf_file.unlink()
                except OSError as cleanup_exc:
                    logger.warning(
                        "Failed to delete temporary PDF %s: %s",
                        pdf_file,
                        cleanup_exc,
                        exc_info=True,
                    )

    @staticmethod
    async def _fetch_arxiv_pdf(arxiv_id: str) -> Path:
        url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            content = resp.content

        # Create unique file name to avoid race conditions if two processes handle the same paper
        safe_id = arxiv_id.replace("/", "_")
        out_path = TMP_DIR / f"{safe_id}_{uuid.uuid4().hex}.pdf"

        with open(out_path, "wb") as f:
            f.write(content)
        return out_path

    @staticmethod
    def _pdf_to_text(pdf_path: Path) -> str:
        reader = PdfReader(str(pdf_path))

        parts = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")

        text = "\n".join(parts)
        return text.replace("\r", "\n")
