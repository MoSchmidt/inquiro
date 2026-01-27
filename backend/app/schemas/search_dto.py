from __future__ import annotations

from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, Field, model_validator

from app.schemas.paper_dto import PaperDto


class TextCondition(BaseModel):
    """Single text-based filter condition on a paper field."""

    type: Literal["condition"]
    field: Literal["title", "abstract"]
    operator: Literal["contains", "not_contains"]
    value: str


class ConditionGroup(BaseModel):
    """Logical group combining multiple conditions with AND / OR."""

    type: Literal["group"]
    operator: Literal["AND", "OR"]
    children: List[
        Annotated[Union[TextCondition, ConditionGroup], Field(discriminator="type")]
    ]


class AdvancedSearchFilter(BaseModel):
    """Structured filter with optional year range and boolean condition tree."""

    year_from: Optional[int] = Field(default=None, ge=1, le=9999)
    year_to: Optional[int] = Field(default=None, ge=1, le=9999)
    root: ConditionGroup

    @model_validator(mode="after")
    def check_year_range(self) -> AdvancedSearchFilter:
        if self.year_from is not None and self.year_to is not None:
            if self.year_from > self.year_to:
                raise ValueError("year_from must be <= year_to")
        return self


class SearchRequest(BaseModel):
    """
    Request to search for specified query
    """

    query: str
    filter: Optional[AdvancedSearchFilter] = None


class SearchResponse(BaseModel):
    """
    Response to search for specified query
    """

    papers: List[PaperDto]
