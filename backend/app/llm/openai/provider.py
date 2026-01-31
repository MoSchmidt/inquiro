import json
from typing import Any, Dict, List, Optional, cast

from openai import AsyncOpenAI

from app.core.config import settings
from app.llm.openai.prompts import (
    CHAT_PROMPT,
    KEYWORD_PROMPT,
    PDF_KEYWORD_PROMPT,
    SUMMARIZATION_PROMPT,
)


class OpenAIProvider:
    """Wrapper around the OpenAI client."""

    _model: str

    def __init__(self) -> None:
        if settings.OPENAI_API_KEY is None:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Please configure it in your environment."
            )

        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = "gpt-4o-mini"

    async def extract_keywords(self, user_text: str) -> List[str]:
        """
        Extracts a list of keywords from a given user text using the OpenAI model.
        Returns a list of strings. If parsing fails, returns an empty list.
        """

        response = await self.client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": KEYWORD_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_text,
                },
            ],
        )

        try:
            keyword_list = json.loads(response.choices[0].message.content or "[]")
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

        response = await self.client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": PDF_KEYWORD_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_content,
                },
            ],
        )

        try:
            keyword_list = json.loads(response.choices[0].message.content or "[]")
        except json.decoder.JSONDecodeError:
            keyword_list = []

        return keyword_list

    async def summarise_paper(self, paper_text: str, query: str) -> Dict[str, Any]:
        """
        Creates a summary of a scientific paper.
        Dynamically adjusts schema to include 'relevance_to_query' only if a query is present.
        """
        has_query = query and query.strip()

        properties = {
            "title": {"type": "string"},
            "executive_summary": {"type": "string"},
            "methodology_points": {"type": "array", "items": {"type": "string"}},
            "results_points": {"type": "array", "items": {"type": "string"}},
            "limitations": {"type": "string"},
        }

        required_fields = [
            "title",
            "executive_summary",
            "methodology_points",
            "results_points",
        ]

        if has_query:
            properties["relevance_to_query"] = {"type": "string"}
            required_fields.append("relevance_to_query")

        schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": properties,
            "required": required_fields,
        }

        prompt_content = SUMMARIZATION_PROMPT
        if has_query:
            prompt_content += f"\n\nUser query: {query}"

        response = await self.client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": prompt_content,
                },
                {
                    "role": "user",
                    "content": paper_text,
                },
            ],
            response_format={"type": "json_object"},
        )

        try:
            data = json.loads(response.choices[0].message.content or "{}")
        except (json.decoder.JSONDecodeError, KeyError):
            data = {
                "title": "Summary (Parsing Fallback)",
                "executive_summary": (response.choices[0].message.content or "").strip(),
                "methodology_points": [],
                "results_points": [],
                "limitations": "Parsing failed.",
            }
            if has_query:
                data["relevance_to_query"] = "Could not parse specific section."

        return data

    async def chat_about_paper(
        self, paper_text: str, user_query: str, chat_history: List[Dict[str, str]]
    ) -> str:
        """
        Handles a chat turn using the full paper text as context.
        """

        messages: List[Dict[str, str]] = [
            {"role": "system", "content": CHAT_PROMPT},
            {"role": "system", "content": f"RESEARCH PAPER TEXT:\n\n{paper_text}"},
        ]

        if chat_history:
            messages.extend(chat_history)

        messages.append({"role": "user", "content": user_query})

        response = await self.client.chat.completions.create(
            model=self._model, messages=cast(Any, messages)
        )

        return (response.choices[0].message.content or "").strip()
