from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.responses import FileResponse
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
    response_class=FileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the PDF of the specified paper",
)
async def get_paper_pdf(
    paper_id: int, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)
) -> FileResponse:
    """
    Stream the PDF file of the specified paper.
    This URL can be used directly as the source for frontend PDF viewers.
    """
    # 1. Get path to the temp file from service
    file_path = await PaperService.get_paper_pdf(paper_id=paper_id, session=db)

    # 2. Schedule file deletion to run AFTER the response is sent
    # This prevents the tmp folder from filling up with PDFs
    background_tasks.add_task(
        lambda p: p.unlink(missing_ok=True) if p.exists() else None, file_path
    )

    # 3. Return the file with correct MIME type
    # 'inline' allows it to be displayed in the browser/viewer rather than forcing a download
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=paper_{paper_id}.pdf"},
    )
