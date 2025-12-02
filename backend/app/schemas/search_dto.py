from typing import List

from pydantic import BaseModel

from app.schemas.paper_dto import PaperDto


class SearchRequest(BaseModel):
    """
    Request to search for specified query
    """

    query: str


class SearchResponse(BaseModel):
    """
    Response to search for specified query
    """

    papers: List[PaperDto]
