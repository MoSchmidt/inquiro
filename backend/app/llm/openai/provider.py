import json
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from app.core.config import settings
from app.llm.openai.prompts import KEYWORD_PROMPT, PDF_KEYWORD_PROMPT, SUMMARIZATION_PROMPT


class OpenAIProvider:
    """Wrapper around the OpenAI client."""

    _model: str

    def __init__(self) -> None:
        if settings.OPENAI_API_KEY is None:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Please configure it in your environment."
            )

        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = "gpt-5-nano-2025-08-07"

    async def extract_keywords(self, user_text: str) -> List[str]:
        """
        Extracts a list of keywords from a given user text using the OpenAI model.
        Returns a list of strings. If parsing fails, returns an empty list.
        """

        response = await self.client.responses.create(
            model=self._model,
            reasoning={"effort": "low"},
            input=[
                {
                    "role": "developer",
                    "content": KEYWORD_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_text,
                },
            ],
        )

        try:
            keyword_list = json.loads(response.output_text)
        except json.decoder.JSONDecodeError:
            keyword_list = []

        return keyword_list

    async def extract_keywords_from_pdf(
        self,
        pdf_text: str,
        query: Optional[str] = None,
    ) -> List[str]:
        """
        Extracts a list of search queries from the full text of a paper and an optional query.
        Returns a list of strings.
        """
        user_focus = query or "N/A"

        user_content = f"User focus (optional): {user_focus}\n\n" f"Paper text: \n{pdf_text}"

        response = await self.client.responses.create(
            model=self._model,
            reasoning={"effort": "medium"},
            input=[
                {
                    "role": "developer",
                    "content": PDF_KEYWORD_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_content,
                },
            ],
        )

        try:
            keyword_list = json.loads(response.output_text)
        except json.decoder.JSONDecodeError:
            keyword_list = []

        return keyword_list

    async def summarise_paper(self, paper_text: str, query: str) -> Dict[str, Any]:
        """
        Creates a summary of a scientific paper using the query for context using the OpenAI model.
        Returns a string. If parsing fails, returns an empty string.
        """
        schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "format": {"type": "string", "enum": ["md+tex"]},
                "summary_markdown": {"type": "string"},
            },
            "required": ["format", "summary_markdown"],
        }

        response = await self.client.responses.create(
            model=self._model,
            reasoning={"effort": "medium"},
            input=[
                {
                    "role": "developer",
                    "content": f"{SUMMARIZATION_PROMPT}\n\nUser query: {query}",
                },
                {
                    "role": "user",
                    "content": paper_text,
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "paper_summary",
                    "schema": schema,
                    "strict": True,
                }
            },
        )

        try:
            data = json.loads(response.output_text)
        except (json.decoder.JSONDecodeError, KeyError):
            data = {
                "format": "md+tex",
                "summary_markdown": response.output_text.strip(),
            }

        return data
