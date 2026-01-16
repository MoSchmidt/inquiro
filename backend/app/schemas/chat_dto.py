from typing import List

from pydantic import BaseModel, Field


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
