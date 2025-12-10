from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.paper_dto import PaperSummaryRequest, PaperSummaryResponse
from app.services.paper_service import PaperService

router = APIRouter(prefix="/papers", tags=["Paper"])


@router.post(
    "{paper_id}/summary",
    response_model=PaperSummaryResponse,
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
    return PaperSummaryResponse.model_validate(result)


@router.get(
    "/{paper_id}/pdf",
    response_class=Response,  # <--- Changed: Uses generic Response for bytes
    status_code=status.HTTP_200_OK,
    summary="Get the PDF of the specified paper",
)
async def get_paper_pdf(
    paper_id: int,
    db: AsyncSession = Depends(get_db),  # <--- Changed: Removed BackgroundTasks
) -> Response:
    """
    Returns the PDF bytes of the specified paper.
    This URL can be used directly as the source for frontend PDF viewers.
    """
    # 1. Get raw bytes from service
    pdf_bytes = await PaperService.get_paper_pdf(paper_id=paper_id, session=db)

    # 2. Return bytes with correct MIME type
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=paper_{paper_id}.pdf"},
    )
