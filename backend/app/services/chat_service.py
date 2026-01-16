import logging
from typing import Dict, List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_openai_provider
from app.repositories.paper_repository import PaperRepository
from app.services.paper_service import PaperService
from app.utils.pdf_utils import pdf_bytes_to_text
from app.utils.token_utils import ensure_fits_token_limit

logger = logging.getLogger("inquiro")


class ChatService:
    """Service for session-based chatting with papers."""

    MAX_INPUT_TOKENS = 280_000

    @staticmethod
    async def get_answer(
        paper_id: int, user_query: str, history: List[Dict[str, str]], session: AsyncSession
    ) -> str:
        # 1. Retrieve paper metadata to get external_id
        paper = await PaperRepository.get_paper_by_id(session, paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")

        # 2. Fetch and extract text (Same pattern as PaperService)
        try:
            pdf_bytes = await PaperService._fetch_arxiv_pdf(arxiv_id=paper.paper_id_external)
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

        except Exception:
            logger.exception("Chat error for paper %s", paper.paper_id_external)
            raise HTTPException(status_code=500, detail="Failed to generate AI response.")
