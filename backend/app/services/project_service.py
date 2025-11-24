from typing import Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.models import Paper
from app.repositories.project_repository import ProjectRepository
from app.schemas.generic import SortRequestDto, SearchTextRequestDto
from app.schemas.project_dto import PapersPageResponse, PaperOverviewDto


class ProjectService:

    @staticmethod
    async def list_project_papers(
            session: AsyncSession,
            project_id: int,
            user_id: int,
            page_number: int,
            page_size: int,
            sort: SortRequestDto | None = None,
            search: SearchTextRequestDto | None = None,
    ) -> PapersPageResponse:

        await ProjectService._validate_project_access(
            session=session,
            project_id=project_id,
            user_id=user_id,
        )

        papers = await ProjectRepository.fetch_project_papers(
            session=session,
            project_id=project_id,
            page_number=page_number,
            page_size=page_size,
            sort=sort,
            search=search,
        )

        paper_dtos = ProjectService._to_overview_dtos(papers)

        return PapersPageResponse(
            page_number=page_number,
            page_size=page_size,
            papers=paper_dtos,
        )

    # ───────────────────────────────────────────────
    # Helper methods
    # ───────────────────────────────────────────────

    @staticmethod
    async def _validate_project_access(
            session: AsyncSession,
            project_id: int,
            user_id: int,
    ) -> None:
        """Ensure: project exists AND user is owner."""
        exists = await ProjectRepository.exists(session, project_id)
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

        is_owner = await ProjectRepository.is_user_project_owner(
            session, project_id, user_id
        )
        if not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this project.",
            )

    @staticmethod
    def _to_overview_dtos(papers: Sequence[Paper]) -> list[PaperOverviewDto]:
        """Convert list of Paper ORM objects into DTOs."""
        items: list[PaperOverviewDto] = []

        for p in papers:
            authors_str = ""
            if p.authors:
                # your authors JSON may differ (e.g. {"authors": ["a","b"]})
                arr = p.authors.get("authors", [])
                authors_str = ", ".join(arr)

            items.append(
                PaperOverviewDto(
                    title=p.title,
                    year=p.published_at.year if p.published_at else None,
                    authors=authors_str,
                    published_at=str(p.published_at) if p.published_at else None,
                )
            )
        return items
