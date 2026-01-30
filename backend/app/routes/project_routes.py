from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.schemas.project_dto import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    ProjectWithPapersResponse,
)
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get(
    "",
    response_model=list[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="List projects of the current user",
)
async def list_projects(
        current_user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
) -> list[ProjectResponse]:
    """Return all projects for the authenticated user."""

    return await ProjectService.list_projects(db, current_user_id)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
)
async def create_project(
        payload: ProjectCreate,
        current_user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """Create a new project for the authenticated user."""

    return await ProjectService.create_project(db, current_user_id, payload)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a project",
)
async def update_project(
        project_id: int,
        payload: ProjectUpdate,
        current_user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """Update the metadata of a project (e.g., name)."""

    return await ProjectService.update_project(db, current_user_id, project_id, payload)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project",
)
async def delete_project(
        project_id: int,
        current_user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a project and its stored paper links."""

    await ProjectService.delete_project(db, current_user_id, project_id)


# ------------------------------
# Papers of Project
# ------------------------------
@router.get(
    "/{project_id}/papers",
    summary="Get the paper for a project.",
    response_model=ProjectWithPapersResponse,
)
async def get_papers_for_project(
        project_id: int,
        db: AsyncSession = Depends(get_db),
        current_user_id: int = Depends(get_current_user_id),
) -> ProjectWithPapersResponse:
    """Retrieve all papers for a project."""
    return await ProjectService.list_project_papers(
        session=db,
        user_id=current_user_id,
        project_id=project_id,
    )


@router.post(
    "/{project_id}/papers/{paper_id}",
    response_model=ProjectWithPapersResponse,
    status_code=status.HTTP_200_OK,
    summary="Add a paper to a project",
)
async def add_paper_to_project(
        project_id: int,
        paper_id: int,
        current_user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
) -> ProjectWithPapersResponse:
    """Store a reference to an existing paper in the given project."""

    return await ProjectService.add_paper_to_project(db, current_user_id, project_id, paper_id)


@router.delete(
    "/{project_id}/papers/{paper_id}",
    response_model=ProjectWithPapersResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove a paper from a project",
)
async def remove_paper_from_project(
        project_id: int,
        paper_id: int,
        current_user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
) -> ProjectWithPapersResponse:
    """Remove a stored paper reference from the given project."""

    return await ProjectService.remove_paper_from_project(db, current_user_id, project_id, paper_id)
