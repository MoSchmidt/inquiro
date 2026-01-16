from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.chat_dto import PaperChatRequest, PaperChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/papers", tags=["Paper Chat"])


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
    Context is derived from the full PDF text and optional chat history.
    """

    # 1. Convert DTO history to list of dicts for the OpenAI Provider
    history_dicts = [m.model_dump() for m in request.history]

    # 2. Call the ChatService (which handles the PDF logic and LLM call)
    ai_answer = await ChatService.get_answer(
        paper_id=paper_id, user_query=request.message, history=history_dicts, session=db
    )

    # 3. Return the structured response
    return PaperChatResponse(answer=ai_answer)
