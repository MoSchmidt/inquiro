from typing import List, Optional, Any
from pydantic import BaseModel, Field


class Version(BaseModel):
    """Represents one item in the versions array."""
    version: Optional[str] = Field(default=None)
    submitted_date: Optional[str] = Field(default=None)
    # Additional fields are allowed; arXiv version items vary
    class Config:
        extra = "allow"


class ArxivRecord(BaseModel):
    id: str
    submitter: Optional[str]
    authors: Optional[str]
    title: Optional[str]
    comments: Optional[str]
    journal_ref: Optional[str] = Field(alias="journal-ref")
    doi: Optional[str]
    report_no: Optional[str] = Field(alias="report-no")
    categories: Optional[str]
    license: Optional[str]
    abstract: Optional[str]
    update_date: Optional[str]
    versions: Optional[List[Version]]
    authors_parsed: Optional[List[Any]]  # can be modeled more strictly later

    class Config:
        populate_by_name = True
        extra = "ignore"
