import logging

from app.core.config import settings
from app.core.deps import get_openai_provider

logger = logging.getLogger("inquiro")


class SafetyService:
    """
    Centralized security service for GenAI interactions.
    Implements defenses against Prompt Injection and Toxicity.
    """

    @staticmethod
    def validate_output(text: str) -> bool:
        """
        Run output guardrails. Return true if safe, false if violated
        """
        if settings.SAFETY_CANARY == "":
            logger.error("Safety Canary not set.")
            return False

        if settings.SAFETY_CANARY in text:
            logger.critical("Safety: PROMPT LEAKAGE DETECTED. Canary token found in output.")
            return False

        return True

    @staticmethod
    async def check_moderation(input_text: str) -> bool:
        """
        Checks text against OpenAI's moderation endpoint.
        Returns True if SAFE, False if FLAGGED (toxic).
        """
        openai_provider = get_openai_provider()

        return await openai_provider.check_moderation(input_text)
