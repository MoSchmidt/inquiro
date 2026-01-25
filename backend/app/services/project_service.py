import logging
import re
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Project
from app.repositories.project_repository import ProjectRepository
from app.schemas.paper_dto import PaperDto
from app.schemas.project_dto import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    ProjectWithPapersResponse,
)
from app.services.paper_content_service import PaperContentService
from app.utils.author_utils import normalize_authors

logger = logging.getLogger("inquiro")


class ProjectService:
    """Service for managing user projects and their stored papers."""

    # ------------------------------------------------------------------
    # Project CRUD + details
    # ------------------------------------------------------------------
    @staticmethod
    async def list_projects(
        session: AsyncSession,
        user_id: int,
    ) -> List[ProjectResponse]:
        """List all projects owned by the given user."""
        projects = await ProjectRepository.list_for_user(session, user_id)
        return [ProjectResponse.model_validate(p) for p in projects]

    @staticmethod
    async def create_project(
        session: AsyncSession,
        user_id: int,
        payload: ProjectCreate,
    ) -> ProjectResponse:
        """Create a new project for the given user."""
        ProjectService._validate_project_name(payload.project_name)

        project = await ProjectRepository.create_for_user(session, user_id, payload.project_name)

        return ProjectResponse.model_validate(project)

    @staticmethod
    async def update_project(
        session: AsyncSession,
        user_id: int,
        project_id: int,
        payload: ProjectUpdate,
    ) -> ProjectResponse:
        """Update metadata of an existing project."""
        await ProjectService._validate_project_access(session, project_id, user_id)

        project = await ProjectRepository.get(session, project_id)

        if payload.project_name is not None:
            ProjectService._validate_project_name(payload.project_name)
            project = await ProjectRepository.update_name(session, project, payload.project_name)

        return ProjectResponse.model_validate(project)

    @staticmethod
    async def delete_project(
        session: AsyncSession,
        user_id: int,
        project_id: int,
    ) -> None:
        """Delete a project that belongs to the given user."""
        # Enforce 404 vs 403 semantics
        await ProjectService._validate_project_access(session, project_id, user_id)

        await ProjectRepository.delete(session, project_id)

    # ------------------------------------------------------------------
    # Project papers: listing / paging / search
    # ------------------------------------------------------------------
    @staticmethod
    async def list_project_papers(
        session: AsyncSession,
        project_id: int,
        user_id: int,
    ) -> ProjectWithPapersResponse:
        """Load all papers for a project."""
        await ProjectService._validate_project_access(session, project_id, user_id)

        project = await ProjectRepository.get_with_papers(session, project_id)

        return ProjectService._build_project_with_papers_response(project)

    # ------------------------------------------------------------------
    # Project papers: add / remove
    # ------------------------------------------------------------------
    @staticmethod
    async def add_paper_to_project(
        session: AsyncSession,
        user_id: int,
        project_id: int,
        paper_id: int,
    ) -> ProjectWithPapersResponse:
        """
        Add a paper reference to the given project.

        Also triggers PDF-to-markdown conversion in the background for preemptive caching.
        """

        await ProjectService._validate_project_access(session, project_id, user_id)

        try:
            project = await ProjectRepository.add_paper(
                session,
                project_id=project_id,
                paper_id=paper_id,
            )
        except ValueError as exc:
            # Currently only "Project not found" / "Paper not found"
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc

        # Trigger PDF conversion in background (fire-and-forget)
        try:
            await PaperContentService.trigger_conversion(paper_id, session)
        except Exception as e:
            # Don't fail the add operation if conversion trigger fails
            logger.error("Failed to trigger conversion for paper %d: %s", paper_id, e)

        return ProjectService._build_project_with_papers_response(project)

    @staticmethod
    async def remove_paper_from_project(
        session: AsyncSession,
        user_id: int,
        project_id: int,
        paper_id: int,
    ) -> ProjectWithPapersResponse:
        """Remove a paper reference from the given project."""
        await ProjectService._validate_project_access(session, project_id, user_id)

        try:
            project = await ProjectRepository.remove_paper(
                session,
                project_id=project_id,
                paper_id=paper_id,
            )
        except ValueError as exc:
            # Currently only "Project not found" / "Paper not found"
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc

        return ProjectService._build_project_with_papers_response(project)

    # ------------------------------------------------------------------
    # Helper methods (access checks, mapping, users)
    # ------------------------------------------------------------------
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

        is_owner = await ProjectRepository.is_user_project_owner(session, project_id, user_id)
        if not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this project.",
            )

    @staticmethod
    def _build_project_with_papers_response(
        project: Project,
    ) -> ProjectWithPapersResponse:
        """Map a Project ORM entity (with .papers) to a response DTO."""
        papers = ProjectService._build_paper_summaries(project)
        return ProjectWithPapersResponse(
            project=ProjectResponse.model_validate(project),
            papers=papers,
        )

    @staticmethod
    def _build_paper_summaries(
        project: Project,
    ) -> list[PaperDto]:
        """Convert project.papers into PaperDtos."""
        summaries: list[PaperDto] = []
        for paper in project.papers:
            authors_value = normalize_authors(paper.authors)
            summaries.append(
                PaperDto(
                    paper_id=paper.paper_id,
                    doi=paper.doi,
                    title=paper.title,
                    source=str(paper.source),
                    authors=authors_value,
                    paper_type=str(paper.paper_type),
                    abstract=paper.abstract,
                    published_at=paper.published_at,
                )
            )
        return summaries

    @staticmethod
    def _validate_project_name(name: str) -> None:
        """Ensure valid project name."""
        name_pattern = re.compile(r"^(?=.{1,100}$)[A-Za-z0-9 _-]+$")
        if not name_pattern.fullmatch(name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project name must be 1-100 characters and can only contain letters,"
                " numbers, spaces, underscores, and hyphens.",
            )
