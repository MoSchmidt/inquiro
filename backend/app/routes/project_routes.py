from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
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
def list_projects(
    current_username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ProjectResponse]:
    """Return all projects for the authenticated user."""

    return ProjectService.list_projects(db, current_username)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
)
def create_project(
    payload: ProjectCreate,
    current_username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """Create a new project for the authenticated user."""

    return ProjectService.create_project(db, current_username, payload)


@router.get(
    "/{project_id}",
    response_model=ProjectWithPapersResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a project with its stored papers",
)
def get_project(
    project_id: int,
    current_username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectWithPapersResponse:
    """Return a single project and all papers stored in it."""

    return ProjectService.get_project_with_papers(db, current_username, project_id)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a project",
)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    current_username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """Update the metadata of a project (e.g., name)."""

    return ProjectService.update_project(db, current_username, project_id, payload)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project",
)
def delete_project(
    project_id: int,
    current_username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete a project and its stored paper links."""

    ProjectService.delete_project(db, current_username, project_id)


@router.post(
    "/{project_id}/papers",
    response_model=ProjectWithPapersResponse,
    status_code=status.HTTP_200_OK,
    summary="Add a paper to a project",
)
def add_paper_to_project(
    project_id: int,
    paper_id: int,
    current_username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectWithPapersResponse:
    """Store a reference to an existing paper in the given project."""

    return ProjectService.add_paper_to_project(
        db, current_username, project_id, paper_id
    )


@router.delete(
    "/{project_id}/papers/{paper_id}",
    response_model=ProjectWithPapersResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove a paper from a project",
)
def remove_paper_from_project(
    project_id: int,
    paper_id: int,
    current_username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectWithPapersResponse:
    """Remove a stored paper reference from the given project."""

    return ProjectService.remove_paper_from_project(
        db, current_username, project_id, paper_id
    )
