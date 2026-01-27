from __future__ import annotations

from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from app.schemas.paper_dto import PaperDto


class TextCondition(BaseModel):
    type: Literal["condition"]
    field: Literal["title", "abstract"]
    operator: Literal["contains", "not_contains"]
    value: str


class ConditionGroup(BaseModel):
    type: Literal["group"]
    operator: Literal["AND", "OR"]
    children: List[
        Annotated[Union[TextCondition, ConditionGroup], Field(discriminator="type")]
    ]


class AdvancedSearchFilter(BaseModel):
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    root: ConditionGroup


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
