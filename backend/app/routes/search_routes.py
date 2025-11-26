from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

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
def search(request: SearchRequest, db: Session = Depends(get_db)) -> SearchResponse:
    """
    Returns a list of papers that match the search query.

    Currently, this returns the 5 most recently fetched papers, regardless
    of the query string.
    """

    return SearchService.search_papers(db, request.query)
