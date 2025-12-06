from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.search_dto import SearchRequest, SearchResponse
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

    Currently, this returns the 5 most recently fetched papers, regardless
    of the query string.
    """

    papers = await SearchService.search_papers(request.query, db)
    return SearchResponse.model_validate(papers)


@router.post(
    "/pdf",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search for papers using a PDF",
)
async def search_by_pdf(
    pdf: UploadFile = File(..., description="Research paper PDF"),
    # Optional: user can also input a query
    query: str | None = Form(
        default=None,
        description="Optional: query specifying what you want to find in relation to the paper",
    ),
    db: AsyncSession = Depends(get_db),
) -> SearchResponse:
    """
    Returns a list of papers that are relevant to the uploaded PDF
    The PDF is analyzed, turned into semantic search queries, and used for vector search on our DB.
    """
    papers = await SearchService.search_papers_from_pdf(
        pdf_file=pdf,
        db=db,
        query=query,
    )
    return SearchResponse.model_validate(papers)
