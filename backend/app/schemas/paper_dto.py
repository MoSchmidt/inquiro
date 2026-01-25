from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PaperDto(BaseModel):
    """
    Representation of a paper (as specified in the DB)
    """

    paper_id: int
    doi: Optional[str]  # DOI is not always reliable or present in the source data
    source: str
    paper_type: str
    title: str
    authors: List[str]
    abstract: Optional[str]
    published_at: Optional[date]

    model_config = ConfigDict(from_attributes=True)


class PaperSummaryRequest(BaseModel):
    """
    Request to summarise a specified paper
    """

    query: str


class PaperSummaryResponse(BaseModel):
    """
    Structured response to summary request.
    Fields contain Markdown + LaTeX strings.
    """

    title: str = Field(..., description="The title of the paper.")

    executive_summary: str = Field(
        ..., description="A high-level, 2-3 sentence overview of the paper's core contribution."
    )

    relevance_to_query: Optional[str] = Field(
        default=None,
        description="Direct answer to how this paper relates to the user's specific query.",
    )

    methodology_points: List[str] = Field(
        ..., description="List of technical steps/architectures (bullet points)."
    )

    results_points: List[str] = Field(
        ..., description="List of quantitative findings or theoretical results (bullet points)."
    )

    limitations: str = Field(
        default="Not explicitly stated.",
        description="Critical analysis of constraints or assumptions.",
    )


class ChatMessageDto(BaseModel):
    """
    Represents a single message in the chat history.
    """

    role: str  # "user" or "assistant"
    content: str


class PaperChatRequest(BaseModel):
    """
    Request to chat about a specific paper.
    """

    message: str
    history: List[ChatMessageDto] = Field(default_factory=list)


class PaperChatResponse(BaseModel):
    """
    The AI generated response for the chat.
    Supports Markdown and LaTeX.
    """

    answer: str = Field(..., description="The AI's response to the user's question.")
