from typing import List

from pydantic import BaseModel, Field

from app.schemas.paper_dto import PaperDto


class SearchRequest(BaseModel):
    """
    Request to search for specified query
    """

    query: str = Field(..., max_length=5000)


class SearchResponse(BaseModel):
    """
    Response to search for specified query
    """

    papers: List[PaperDto]
