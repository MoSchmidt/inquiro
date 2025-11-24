from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import select, func, or_, String
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.sort_constants import SortDirection
from app.models import Project, Paper
from app.schemas.generic import SortRequestDto, SearchTextRequestDto

SORT_FIELD_MAP = {
    "title": Paper.title,
    "year": Paper.published_at,
}


class ProjectRepository:

    @staticmethod
    def build_sort_expression(sort: SortRequestDto):
        if sort and sort.sort_by:
            column = SORT_FIELD_MAP.get(sort.sort_by)
        else:
            column = Paper.paper_id

        if column is None:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort field: {sort.sort_by}"
            )

        if sort.sort_order == SortDirection.ASC:
            return column.asc()

        return column.desc()

    @staticmethod
    async def exists(session: AsyncSession, project_id: int) -> bool:
        stmt = (
            select(func.count())
            .select_from(Project)
            .where(Project.project_id == project_id)
        )
        return (await session.scalar(stmt)) > 0

    @staticmethod
    async def is_user_project_owner(
            session: AsyncSession, project_id: int, user_id: int
    ) -> bool:
        stmt = (
            select(func.count())
            .select_from(Project)
            .where(
                Project.project_id == project_id,
                Project.created_by == user_id,
            )
        )
        return (await session.scalar(stmt)) > 0

    @staticmethod
    async def fetch_project_papers(
            session: AsyncSession,
            project_id: int,
            page_number: int,
            page_size: int,
            sort: SortRequestDto,
            search: SearchTextRequestDto | None,
    ) -> Sequence[Paper]:

        sort_expr = ProjectRepository.build_sort_expression(sort)

        stmt = (
            select(Paper)
            .join(Paper.projects)
            .where(Project.project_id == project_id)
        )

        # Add search filter only if provided and not empty
        if search and search.search_text:
            text = f"%{search.search_text}%"

            stmt = stmt.where(
                or_(
                    Paper.title.ilike(text),
                    Paper.abstract.ilike(text),
                    func.cast(Paper.authors, String).ilike(text),
                )
            )

        stmt = (
            stmt.order_by(sort_expr)
            .offset((page_number - 1) * page_size)
            .limit(page_size)
        )

        result = await session.scalars(stmt)
        return result.all()
