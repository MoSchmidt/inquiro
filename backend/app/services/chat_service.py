import logging
from typing import Dict, List

import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.database_constants import PaperSource
from app.core.deps import get_openai_provider
from app.repositories.paper_repository import PaperRepository
from app.utils.pdf_utils import pdf_bytes_to_text
from app.utils.token_utils import ensure_fits_token_limit

logger = logging.getLogger("inquiro")


class ChatService:
    """
    Service for session-based chatting with papers.
    """

    MAX_INPUT_TOKENS = 280_000

    @staticmethod
    async def get_answer(
        paper_id: int, user_query: str, history: List[Dict[str, str]], session: AsyncSession
    ) -> str:
        """
        Retrieves a paper, extracts its text, and generates an AI response based on chat history.
        Returns the AI-generated string answer.
        """
        # 1. Retrieve paper metadata to get external_id
        paper = await PaperRepository.get_paper_by_id(session, paper_id)

        if not paper:
            logger.warning("Failed to find specified paper in DB: %s", paper_id)
            raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")

        external_id = paper.paper_id_external
        paper_source = paper.source

        if paper_source != PaperSource.ARXIV:
            logger.warning("Unsupported paper source for summarization: %s", paper.source)
            raise HTTPException(
                status_code=422,
                detail=f"Unsupported paper source '{paper_source}'. Only ARXIV is supported.",
            )

        # 2. Fetch and extract text
        try:
            pdf_bytes = await ChatService._fetch_arxiv_pdf(arxiv_id=external_id)
            pdf_text = pdf_bytes_to_text(pdf_bytes)

            ensure_fits_token_limit(
                pdf_text,
                max_tokens=ChatService.MAX_INPUT_TOKENS,
                error_status=413,
                error_detail="Paper content exceeds context limits.",
            )

            # 3. Get AI response using the history provided by the frontend
            openai_provider = get_openai_provider()
            answer = await openai_provider.chat_about_paper(
                paper_text=pdf_text, user_query=user_query, chat_history=history
            )

            return answer

        except Exception as exc:
            logger.exception("Chat error for paper %s", external_id)
            raise HTTPException(status_code=500, detail="Failed to generate AI response.") from exc

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
