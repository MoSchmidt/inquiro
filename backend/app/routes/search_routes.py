import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.search_dto import AdvancedSearchFilter, SearchRequest, SearchResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])


@router.post(
    "",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search for papers",
)
async def search(request: SearchRequest, db: AsyncSession = Depends(get_db)) -> SearchResponse:
    """
    Returns a list of papers that match the search query.
    Optionally accepts an advanced filter with year range and text conditions.
    """

    papers = await SearchService.search_papers(
        query=request.query,
        db=db,
        search_filter=request.filter,
    )
    return SearchResponse.model_validate(papers)


@router.post(
    "/pdf",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search for papers using a PDF",
)
async def search_by_pdf(
    pdf: UploadFile = File(..., description="Research paper PDF"),
    query: str | None = Form(
        default=None,
        description="Optional: query specifying what you want to find in relation to the paper",
    ),
    filter: str | None = Form(
        default=None,
        description="Optional: JSON-encoded advanced search filter",
    ),
    db: AsyncSession = Depends(get_db),
) -> SearchResponse:
    """
    Returns a list of papers that are relevant to the uploaded PDF.
    The PDF is analyzed, turned into semantic search queries, and used for vector search on our DB.
    Optionally accepts a JSON-encoded advanced filter.
    """
    if pdf.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Invalid file type: Only PDF files are supported.",
        )

    search_filter = None
    if filter:
        try:
            search_filter = AdvancedSearchFilter.model_validate(json.loads(filter))
        except (json.JSONDecodeError, ValueError) as exc:
            raise HTTPException(
                status_code=400,
                detail="Invalid filter JSON.",
            ) from exc

    papers = await SearchService.search_papers_from_pdf(
        pdf_file=pdf,
        db=db,
        query=query,
        search_filter=search_filter,
    )
    return SearchResponse.model_validate(papers)
