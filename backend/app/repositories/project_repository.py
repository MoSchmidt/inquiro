from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.paper import Paper
from app.models.project import Project
from app.models.project_paper import ProjectPaper


class ProjectRepository:
    """Repository for project and project-paper related operations."""

    @staticmethod
    def list_for_user(db: Session, user_id: int) -> List[Project]:
        """Return all projects owned by the given user."""
        return (
            db.query(Project)
            .filter(Project.created_by == user_id)
            .order_by(Project.created_at.desc())
            .all()
        )

    @staticmethod
    def get_for_user(db: Session, project_id: int, user_id: int) -> Optional[Project]:
        """Return a single project if it belongs to the given user."""
        return (
            db.query(Project)
            .filter(Project.project_id == project_id, Project.created_by == user_id)
            .first()
        )

    @staticmethod
    def create_for_user(db: Session, user_id: int, project_name: str) -> Project:
        """Create a new project for the given user."""
        project = Project(created_by=user_id, project_name=project_name)
        db.add(project)
        db.commit()
        db.refresh(project, attribute_names=["papers"])
        return project

    @staticmethod
    def update_name(db: Session, project: Project, new_name: str) -> Project:
        """Update the project's name."""
        project.project_name = new_name
        db.add(project)
        db.commit()
        db.refresh(project, attribute_names=["papers"])
        return project

    @staticmethod
    def delete_for_user(db: Session, project_id: int, user_id: int) -> None:
        """Delete a project owned by the given user."""
        project = ProjectRepository.get_for_user(db, project_id, user_id)
        if project is None:
            raise ValueError("Project not found or not owned by user")
        db.delete(project)
        db.commit()

    @staticmethod
    def add_paper(db: Session, project_id: int, paper_id: int, user_id: int) -> Project:
        """Add a paper to a project if not already linked."""
        project = ProjectRepository.get_for_user(db, project_id, user_id)
        if project is None:
            raise ValueError("Project not found or not owned by user")

        paper = db.query(Paper).filter(Paper.paper_id == paper_id).first()
        if paper is None:
            raise ValueError("Paper not found")

        existing_link = (
            db.query(ProjectPaper)
            .filter(
                ProjectPaper.project_id == project_id,
                ProjectPaper.paper_id == paper_id,
            )
            .first()
        )
        if existing_link is None:
            link = ProjectPaper(project_id=project_id, paper_id=paper_id)
            db.add(link)
            db.commit()

        db.refresh(project, attribute_names=["papers"])
        return project

    @staticmethod
    def remove_paper(db: Session, project_id: int, paper_id: int, user_id: int) -> Project:
        """Remove a paper from a project."""
        project = ProjectRepository.get_for_user(db, project_id, user_id)
        if project is None:
            raise ValueError("Project not found or not owned by user")

        link = (
            db.query(ProjectPaper)
            .filter(
                ProjectPaper.project_id == project_id,
                ProjectPaper.paper_id == paper_id,
            )
            .first()
        )
        if link is not None:
            db.delete(link)
            db.commit()

        db.refresh(project, attribute_names=["papers"])
        return project
