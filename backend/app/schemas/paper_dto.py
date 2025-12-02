from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class PaperDto(BaseModel):
    """
    Representation of a paper (as specified in the DB)
    """

    paper_id: int
    doi: Optional[str]  # DOI is not always reliable or present in the source data
    source: str
    paper_type: str
    title: str
    authors: List[str]
    abstract: Optional[str]
    published_at: Optional[date]

    model_config = ConfigDict(from_attributes=True)


class PaperSummaryRequest(BaseModel):
    """
    Request to summarise a specified paper
    """

    paper_id: int
    query: str


class PaperSummaryResponse(BaseModel):
    """
    Response to summary request for a specified paper
    """

    summary: str
