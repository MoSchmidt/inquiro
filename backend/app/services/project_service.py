from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository
from app.schemas.project_dto import (
    PaperSummary,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    ProjectWithPapersResponse,
)


class ProjectService:
    """Service for managing user projects and their stored papers."""

    @staticmethod
    def _get_user(db: Session, username: str) -> User:
        """Return the user for the given username or raise 404."""
        user = UserRepository.get_by_username(db, username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        return user

    @staticmethod
    def list_projects(db: Session, username: str) -> List[ProjectResponse]:
        """List all projects owned by the given user."""
        user = ProjectService._get_user(db, username)
        projects = ProjectRepository.list_for_user(db, user.user_id)
        return [ProjectResponse.model_validate(p) for p in projects]

    @staticmethod
    def get_project_with_papers(
        db: Session, username: str, project_id: int
    ) -> ProjectWithPapersResponse:
        """Return a single project and all of its stored papers."""
        user = ProjectService._get_user(db, username)
        project = ProjectRepository.get_for_user(db, project_id, user.user_id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

        papers = [PaperSummary.model_validate(p) for p in project.papers]
        return ProjectWithPapersResponse(
            project=ProjectResponse.model_validate(project),
            papers=papers,
        )

    @staticmethod
    def create_project(
        db: Session, username: str, payload: ProjectCreate
    ) -> ProjectResponse:
        """Create a new project for the given user."""
        user = ProjectService._get_user(db, username)
        project = ProjectRepository.create_for_user(
            db, user.user_id, payload.project_name
        )
        return ProjectResponse.model_validate(project)

    @staticmethod
    def update_project(
        db: Session, username: str, project_id: int, payload: ProjectUpdate
    ) -> ProjectResponse:
        """Update metadata of an existing project."""
        user = ProjectService._get_user(db, username)
        project = ProjectRepository.get_for_user(db, project_id, user.user_id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

        if payload.project_name is not None:
            project = ProjectRepository.update_name(db, project, payload.project_name)
        return ProjectResponse.model_validate(project)

    @staticmethod
    def delete_project(db: Session, username: str, project_id: int) -> None:
        """Delete a project that belongs to the given user."""
        user = ProjectService._get_user(db, username)
        project = ProjectRepository.get_for_user(db, project_id, user.user_id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )
        ProjectRepository.delete_for_user(db, project_id, user.user_id)

    @staticmethod
    def add_paper_to_project(
        db: Session, username: str, project_id: int, paper_id: int
    ) -> ProjectWithPapersResponse:
        """Add a paper reference to the given project."""
        user = ProjectService._get_user(db, username)
        try:
            project = ProjectRepository.add_paper(
                db, project_id=project_id, paper_id=paper_id, user_id=user.user_id
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc

        papers = [PaperSummary.model_validate(p) for p in project.papers]
        return ProjectWithPapersResponse(
            project=ProjectResponse.model_validate(project),
            papers=papers,
        )

    @staticmethod
    def remove_paper_from_project(
        db: Session, username: str, project_id: int, paper_id: int
    ) -> ProjectWithPapersResponse:
        """Remove a paper reference from the given project."""
        user = ProjectService._get_user(db, username)
        try:
            project = ProjectRepository.remove_paper(
                db, project_id=project_id, paper_id=paper_id, user_id=user.user_id
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc

        papers = [PaperSummary.model_validate(p) for p in project.papers]
        return ProjectWithPapersResponse(
            project=ProjectResponse.model_validate(project),
            papers=papers,
        )


