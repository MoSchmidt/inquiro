import json
from typing import List

from openai import OpenAI

from app.core.config import settings
from app.llm.openai.prompts import KEYWORD_PROMPT


class OpenAIProvider:
    """Wrapper around the OpenAI client."""

    _model: str

    def __init__(self) -> None:
        if settings.OPENAI_API_KEY is None:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Please configure it in your environment."
            )

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = "gpt-5-nano-2025-08-07"

    def extract_keywords(self, user_text: str) -> List[str]:
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
