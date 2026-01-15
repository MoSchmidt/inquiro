import json
from typing import List

from openai import AsyncOpenAI

from app.core.config import settings
from app.llm.openai.prompts import KEYWORD_PROMPT, SUMMARIZATION_PROMPT

from openai import OpenAI


class OpenAIProvider:
    """Wrapper around the OpenAI client."""

    _model: str

    def __init__(self) -> None:
        if settings.OPENAI_API_KEY is None:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Please configure it in your environment."
            )

        #self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key="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")
        self._model = "openai/gpt-4o-mini"

    async def extract_keywords(self, user_text: str) -> List[str]:
        """
        Extracts a list of keywords from a given user text using the OpenAI model.
        Returns a list of strings. If parsing fails, returns an empty list.
        """

        response = self.client.responses.create(
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

    async def summarise_paper(self, paper_text: str, query: str) -> str:
        """
        Creates a summary of a scientific paper using the query for context using the OpenAI model.
        Returns a string. If parsing fails, returns an empty string.
        """

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
        )

        return response.output_text
