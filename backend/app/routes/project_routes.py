from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_optional_sort, get_optional_search
from app.core.security import get_current_user_id
from app.schemas.generic import SortRequestDto, SearchTextRequestDto
from app.schemas.project_dto import PapersPageResponse
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Project"])


@router.get("/{project_id}/papers", summary="Get a page of papers for a project.", response_model=PapersPageResponse)
async def get_papers_for_project(
        project_id: int,
        page_number: int = 1,
        page_size: int = 20,
        sort: Optional[SortRequestDto] = Depends(get_optional_sort),
        search: Optional[SearchTextRequestDto] = Depends(get_optional_search),
        db: AsyncSession = Depends(get_db),
        current_user_id: int = Depends(get_current_user_id),
) -> PapersPageResponse:
    return await ProjectService.list_project_papers(
        session=db,
        user_id=current_user_id,
        project_id=project_id,
        page_number=page_number,
        page_size=page_size,
        sort=sort,
        search=search
    )
