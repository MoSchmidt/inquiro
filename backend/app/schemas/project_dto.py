from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.paper_dto import PaperDto


class ProjectCreate(BaseModel):
    """Request payload to create a new project."""

    project_name: str


class ProjectUpdate(BaseModel):
    """Request payload to update a project."""

    project_name: Optional[str] = None


class ProjectResponse(BaseModel):
    """Representation of a project."""

    project_id: int
    project_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectWithPapersResponse(BaseModel):
    """Project including its stored papers."""

    project: ProjectResponse
    papers: List[PaperDto]
