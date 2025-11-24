from pydantic import BaseModel

from app.schemas.generic import PageResponseDto


class PaperOverviewDto(BaseModel):
    title: str
    year: int | None = None
    authors: str
    published_at: str | None = None


class PapersPageResponse(PageResponseDto):
    papers: list[PaperOverviewDto]
