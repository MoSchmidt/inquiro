from pydantic import BaseModel

from app.constants.sort_constants import SortDirection


class PageResponseDto(BaseModel):
    page_size: int
    page_number: int


class SortRequestDto(BaseModel):
    sort_by: str
    sort_order: SortDirection


class SearchTextRequestDto(BaseModel):
    search_text: str
