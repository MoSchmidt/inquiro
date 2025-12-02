from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.paper_dto import PaperSummaryRequest, PaperSummaryResponse
from app.services.paper_service import PaperService

router = APIRouter(prefix="/paper", tags=["Paper"])


@router.post(
    "/summary",
    response_model=PaperSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Summarise the specified paper",
)
async def summary(
    request: PaperSummaryRequest, db: AsyncSession = Depends(get_db)
) -> PaperSummaryResponse:
    """
    Returns the summary of the specified paper.
    """

    result = await PaperService.summarise_paper(
        paper_id=request.paper_id, query=request.query, session=db
    )
    return PaperSummaryResponse.model_validate(result)
