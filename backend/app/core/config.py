"""Configuration objects and helpers for the FastAPI application."""

import os
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or ``.env`` files."""

    # --- App Settings ---
    APP_NAME: str = "Inquiro API"
    ENVIRONMENT: str = "dev"

    # --- Database ---
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    DATABASE_URL: str

    # --- JWT / Auth ---
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- OpenAI ---
    OPENAI_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", "dev.env"),
        extra="ignore",
    )


settings = Settings()  # type: ignore[call-arg]
