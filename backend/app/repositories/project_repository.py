from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.paper import Paper
from app.models.project import Project
from app.models.project_paper import ProjectPaper


class ProjectRepository:
    """Repository for project and project-paper related operations."""

    # ------------------------------------------------------------------
    # Project: read operations
    # ------------------------------------------------------------------
    @staticmethod
    async def list_for_user(session: AsyncSession, user_id: int) -> List[Project]:
        """Return all projects owned by the given user."""
        stmt = (
            select(Project)
            .where(Project.created_by == user_id)
            .order_by(Project.created_at.desc())
        )
        result = await session.scalars(stmt)
        return list(result.all())

    @staticmethod
    async def get(
        session: AsyncSession,
        project_id: int,
    ) -> Optional[Project]:
        """Return a single project by id."""
        stmt = select(Project).where(Project.project_id == project_id)
        result = await session.scalars(stmt)
        return result.first()

    @staticmethod
    async def get_with_papers(
        session: AsyncSession,
        project_id: int,
    ) -> Optional[Project]:
        """Return a single project by id, with papers eagerly loaded."""
        stmt = (
            select(Project)
            .options(selectinload(Project.papers))
            .where(Project.project_id == project_id)
        )
        result = await session.scalars(stmt)
        return result.first()

    # ------------------------------------------------------------------
    # Project: lifecycle (create / update / delete)
    # ------------------------------------------------------------------
    @staticmethod
    async def create_for_user(
        session: AsyncSession,
        user_id: int,
        project_name: str,
    ) -> Project:
        """Create a new project for the given user."""
        project = Project(created_by=user_id, project_name=project_name)
        session.add(project)
        await session.commit()
        await session.refresh(project, attribute_names=["papers"])
        return project

    @staticmethod
    async def update_name(
        session: AsyncSession,
        project: Project,
        new_name: str,
    ) -> Project:
        """Update the project's name."""
        project.project_name = new_name
        session.add(project)
        await session.commit()
        await session.refresh(project, attribute_names=["papers"])
        return project

    @staticmethod
    async def delete(
        session: AsyncSession,
        project_id: int,
    ) -> None:
        """Delete a project by id."""
        project = await ProjectRepository.get(session, project_id)
        if project is None:
            raise ValueError("Project not found")

        await session.delete(project)
        await session.commit()

    # ------------------------------------------------------------------
    # Project ↔ Paper links
    # ------------------------------------------------------------------
    @staticmethod
    async def add_paper(
        session: AsyncSession,
        project_id: int,
        paper_id: int,
    ) -> Project:
        """Add a paper to a project if not already linked."""
        project = await ProjectRepository.get_with_papers(session, project_id)
        if project is None:
            raise ValueError("Project not found")

        # Ensure paper exists
        paper_result = await session.scalars(
            select(Paper).where(Paper.paper_id == paper_id)
        )
        paper = paper_result.first()
        if paper is None:
            raise ValueError("Paper not found")

        # Check for existing link
        existing_result = await session.scalars(
            select(ProjectPaper).where(
                ProjectPaper.project_id == project_id,
                ProjectPaper.paper_id == paper_id,
            )
        )
        existing_link = existing_result.first()

        if existing_link is None:
            link = ProjectPaper(project_id=project_id, paper_id=paper_id)
            session.add(link)
            await session.commit()

        await session.refresh(project, attribute_names=["papers"])
        return project

    @staticmethod
    async def remove_paper(
        session: AsyncSession,
        project_id: int,
        paper_id: int,
    ) -> Project:
        """Remove a paper from a project."""
        project = await ProjectRepository.get_with_papers(session, project_id)
        if project is None:
            raise ValueError("Project not found")

        link_result = await session.scalars(
            select(ProjectPaper).where(
                ProjectPaper.project_id == project_id,
                ProjectPaper.paper_id == paper_id,
            )
        )
        link = link_result.first()

        if link is not None:
            await session.delete(link)
            await session.commit()

        await session.refresh(project, attribute_names=["papers"])
        return project

    # ------------------------------------------------------------------
    # Project checks (existence / ownership)
    # ------------------------------------------------------------------
    @staticmethod
    async def exists(session: AsyncSession, project_id: int) -> bool:
        """Return True if a project with the given ID exists."""
        stmt = (
            select(func.count())
            .select_from(Project)
            .where(Project.project_id == project_id)
        )
        count = await session.scalar(stmt) or 0
        return count > 0

    @staticmethod
    async def is_user_project_owner(
            session: AsyncSession,
            project_id: int,
            user_id: int,
    ) -> bool:
        """Return True if the user is the owner of the project."""
        stmt = (
            select(func.count())
            .select_from(Project)
            .where(
                Project.project_id == project_id,
                Project.created_by == user_id,
            )
        )
        count = await session.scalar(stmt) or 0
        return count > 0
