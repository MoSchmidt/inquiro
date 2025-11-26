from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class Paper(BaseModel):
    """
    Representation of a paper (as specified in the DB)
    """

    paper_id: int
    doi: Optional[str]
    source: str
    paper_type: str
    title: str
    authors: Optional[List[List[str]]]
    abstract: Optional[str]
    published_at: Optional[date]
    fetched_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SearchRequest(BaseModel):
    """
    Request to search for specified query
    """

    query: str


class SearchResponse(BaseModel):
    """
    Response to search for specified query
    """

    papers: List[Paper]
