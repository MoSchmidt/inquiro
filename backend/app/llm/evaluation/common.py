"""Common utilities for evaluation scripts."""

import argparse
import logging
from typing import Dict, List, Optional

from app.core.config import settings
from app.llm.openai.provider import OpenAIProvider

logger = logging.getLogger(__name__)


def add_delay_argument(parser: argparse.ArgumentParser) -> None:
    """
    Add the standard --delay argument to an argument parser.

    Args:
        parser: ArgumentParser instance to add the argument to
    """
    parser.add_argument(
        "--delay",
        type=float,
        default=20.0,
        help="Delay in seconds between API requests (default: 20.0 for 3 RPM limit)",
    )


def add_dataset_argument(parser: argparse.ArgumentParser) -> None:
    """
    Add the standard --dataset argument to an argument parser.

    Args:
        parser: ArgumentParser instance to add the argument to
    """
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="Path to dataset JSON file",
    )


def validate_openai_api_key() -> bool:
    """
    Validate that OPENAI_API_KEY is set in the environment.

    Returns:
        True if API key is set, False otherwise
    """
    if settings.OPENAI_API_KEY is None:
        logger.error("OPENAI_API_KEY is not set. Please configure it in your environment.")
        return False
    return True


async def call_openai_api(
    provider: OpenAIProvider,
    developer_prompt: str,
    user_content: Optional[str] = None,
    reasoning_effort: str = "low",
) -> str:
    """
    Make a standardized OpenAI API call for evaluation scripts.

    Args:
        provider: OpenAIProvider instance
        developer_prompt: Prompt for the developer role
        user_content: Optional user content (if None, only developer prompt is sent)
        reasoning_effort: Reasoning effort level (default: "low")

    Returns:
        Response text from the API

    Raises:
        Exception: If the API call fails
    """
    input_messages: List[Dict[str, str]] = [
        {
            "role": "developer",
            "content": developer_prompt,
        },
    ]

    if user_content is not None:
        input_messages.append(
            {
                "role": "user",
                "content": user_content,
            }
        )

    # Accessing _model is necessary for evaluation scripts
    # pylint: disable=protected-access
    response = await provider.client.responses.create(
        model=provider._model,
        reasoning={"effort": reasoning_effort},
        input=input_messages,
    )
    return response.output_text.strip()
