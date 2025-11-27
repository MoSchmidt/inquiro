from pydantic import BaseModel

from app.schemas.generic import PageResponseDto


class PaperOverviewDto(BaseModel):
    title: str
    authors: str
    published_at: str | None = None


class PapersPageResponse(PageResponseDto):
    papers: list[PaperOverviewDto]
