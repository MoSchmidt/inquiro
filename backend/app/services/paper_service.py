import logging
from typing import Dict, List

import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.database_constants import PaperSource
from app.core.deps import get_openai_provider
from app.repositories.paper_repository import PaperRepository
from app.schemas.paper_dto import PaperSummaryResponse
from app.utils.pdf_utils import pdf_bytes_to_text
from app.utils.token_utils import ensure_fits_token_limit

logger = logging.getLogger("inquiro")


class PaperService:
    """
    Service for interacting with research papers (Summarization, Chat, and PDF retrieval)
    """

    # GPT 5 nano has a max. content size of 400k tokens, combining input and output.
    # This represents a conservative estimate, leaving enough space for the prompt and output.
    MAX_INPUT_TOKENS = 280_000

    @staticmethod
    async def summarise_paper(
        paper_id: int, query: str, session: AsyncSession
    ) -> PaperSummaryResponse:
        """
        Retrieves paper specified by id, retrieves its pdf version, and summarises it.
        Returns a summary of the specified paper
        """

        try:
            pdf_text, external_id = await PaperService._prepare_paper_text(paper_id, session)

            openai_provider = get_openai_provider()
            summary_payload = await openai_provider.summarise_paper(pdf_text, query)
            return PaperSummaryResponse.model_validate(summary_payload)
        except httpx.HTTPStatusError as exc:
            # arXiv returned 404 or similar error
            logger.warning("Failed to fetch arXiv paper %s: %s", external_id, exc, exc_info=True)
            raise HTTPException(status_code=404, detail="Paper not found") from exc
        except httpx.RequestError as exc:
            logger.warning(
                "Network error while fetching arXiv paper %s: %s", external_id, exc, exc_info=True
            )
            raise HTTPException(
                status_code=503,
                detail="Upstream arXiv service unavailable, please try again later.",
            ) from exc
        except Exception as exc:
            # Catch-all for unexpected issues (PDF parsing, LLM errors, ...)
            logger.exception("Error summarising arxiv paper %s", external_id)
            raise HTTPException(
                status_code=500, detail="An unexpected error occurred while summarising the paper."
            ) from exc

    @staticmethod
    async def get_chat_answer(
        paper_id: int, user_query: str, history: List[Dict[str, str]], session: AsyncSession
    ) -> str:
        """
        Generates an AI response based on paper content and chat history.
        """
        pdf_text, external_id = await PaperService._prepare_paper_text(paper_id, session)

        try:
            openai_provider = get_openai_provider()
            answer = await openai_provider.chat_about_paper(
                paper_text=pdf_text, user_query=user_query, chat_history=history
            )
            return answer
        except Exception as exc:
            logger.exception("Chat error for paper %s", external_id)
            raise HTTPException(status_code=500, detail="Failed to generate AI response.") from exc

    @staticmethod
    async def get_paper_pdf(paper_id: int, session: AsyncSession) -> bytes:
        """
        Retrieves the PDF bytes for the specified paper.
        Used by the frontend PDF viewer.
        """
        paper = await PaperRepository.get_paper_by_id(session, paper_id)

        if not paper:
            logger.warning("Failed to find specified paper in DB: %s", paper_id)
            raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")

        if paper.source != PaperSource.ARXIV:
            logger.warning("Unsupported paper source for PDF retrieval: %s", paper.source)
            raise HTTPException(
                status_code=422,
                detail=f"Unsupported paper source '{paper.source}'. Only ARXIV is supported.",
            )

        try:
            return await PaperService._fetch_arxiv_pdf(arxiv_id=paper.paper_id_external)
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "Failed to fetch arXiv paper %s: %s",
                paper.paper_id_external,
                exc,
                exc_info=True,
            )
            raise HTTPException(status_code=404, detail="Paper not found") from exc
        except httpx.RequestError as exc:
            logger.warning(
                "Network error while fetching arXiv paper %s: %s",
                paper.paper_id_external,
                exc,
                exc_info=True,
            )
            raise HTTPException(
                status_code=503,
                detail="Upstream arXiv service unavailable, please try again later.",
            ) from exc

    @staticmethod
    async def _prepare_paper_text(paper_id: int, session: AsyncSession) -> (str, str):
        """
        Shared internal logic to fetch paper and prepare text for LLM consumption.
        Returns a tuple of (extracted_text, external_id).
        """
        paper = await PaperRepository.get_paper_by_id(session, paper_id)

        if not paper:
            logger.warning("Failed to find specified paper in DB: %s", paper_id)
            raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")

        # At the moment we only support arXiv as source; if we intend to add papers from different
        # sources, the necessary functions need to be implemented. Until then just return an
        # exception for unsupported sources.
        if paper.source != PaperSource.ARXIV:
            logger.warning("Unsupported paper source for summarization: %s", paper.source)
            raise HTTPException(
                status_code=422,
                detail=f"Unsupported paper source '{paper.source}'. Only ARXIV is supported.",
            )

        pdf_bytes = await PaperService._fetch_arxiv_pdf(arxiv_id=paper.paper_id_external)

        pdf_text = pdf_bytes_to_text(pdf_bytes)

        # If the pdf is of excessive length (> few hundred pages) it is too big for a single
        # request. We could process the paper in multiple parts but that would be a lot of
        # effort for a tiny proportion of all papers.
        ensure_fits_token_limit(
            pdf_text,
            max_tokens=PaperService.MAX_INPUT_TOKENS,
            error_status=413,
            error_detail="Paper content exceeds context limits.",
        )

        return pdf_text, paper.paper_id_external

    @staticmethod
    async def _fetch_arxiv_pdf(arxiv_id: str) -> bytes:
        """
        Fetch arXiv PDF and return its raw bytes.
        """

        url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.content
