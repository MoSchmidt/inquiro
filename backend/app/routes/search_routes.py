from fastapi import APIRouter, Depends, status
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
