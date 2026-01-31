import io
import logging

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.paper_dto import (
    PaperChatRequest,
    PaperChatResponse,
    PaperSummaryRequest,
    PaperSummaryResponse,
)
from app.services.paper_service import PaperService

logger = logging.getLogger("inquiro")

router = APIRouter(prefix="/papers", tags=["Paper"])


@router.post(
    "/{paper_id}/summary",
    response_model=PaperSummaryResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
    summary="Summarise the specified paper",
)
async def summary(
        paper_id: int, request: PaperSummaryRequest, db: AsyncSession = Depends(get_db)
) -> PaperSummaryResponse:
    """
    Returns the summary of the specified paper.
    """
    result = await PaperService.summarise_paper(paper_id=paper_id, query=request.query, session=db)
    return result


@router.post(
    "/{paper_id}/chat",
    response_model=PaperChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat with the specified paper",
)
async def chat_with_paper(
    paper_id: int, request: PaperChatRequest, db: AsyncSession = Depends(get_db)
) -> PaperChatResponse:
    """
    Allows the user to ask questions about the paper currently being viewed.
    """
    history_dicts = [m.model_dump() for m in request.history]

    ai_answer = await PaperService.get_chat_answer(
        paper_id=paper_id, user_query=request.message, history=history_dicts, session=db
    )

    return PaperChatResponse(answer=ai_answer)


@router.get(
    "/{paper_id}/pdf",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the PDF of the specified paper",
)
async def get_paper_pdf(
        paper_id: int,
        db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """
    Stream the PDF file of the specified paper.
    This URL can be used directly as the source for frontend PDF viewers.
    """
    # 1. Get raw bytes from service
    pdf_bytes = await PaperService.get_paper_pdf(paper_id=paper_id, session=db)

    # 2. Wrap bytes in a stream and return StreamingResponse
    # io.BytesIO turns the bytes into a file-like object that StreamingResponse can read
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=paper_{paper_id}.pdf"},
    )
