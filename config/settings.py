"""Runtime settings and shared dependency factories."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from langchain_openai import ChatOpenAI
from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from exceptions import ConfigurationError


class Settings(BaseSettings):
    """Environment-backed application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    serpapi_key: str = Field(default="", alias="SERPAPI_KEY")

    smtp_host: str = Field(default="smtp.gmail.com", alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_user: str = Field(default="", alias="SMTP_USER")
    smtp_password: str = Field(default="", alias="SMTP_PASSWORD")

    db_path: Path = Field(default=Path("data/db/jobs.db"), alias="DB_PATH")
    chroma_path: Path = Field(default=Path("data/db/chroma"), alias="CHROMA_PATH")
    base_resume_path: Path = Field(default=Path("data/resumes/base_resume.pdf"), alias="BASE_RESUME_PATH")

    fastapi_host: str = Field(default="0.0.0.0", alias="FASTAPI_HOST")
    fastapi_port: int = Field(default=8000, alias="FASTAPI_PORT")
    streamlit_port: int = Field(default=8501, alias="STREAMLIT_PORT")

    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.2


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings and ensure data directories exist."""

    settings = Settings()
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    settings.chroma_path.mkdir(parents=True, exist_ok=True)
    return settings


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    """Create a single ChatOpenAI client shared across modules."""

    settings = get_settings()
    if not settings.openai_api_key:
        raise ConfigurationError("OPENAI_API_KEY is missing in environment configuration.")

    logger.debug("Initializing ChatOpenAI model: {}", settings.llm_model)
    return ChatOpenAI(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        api_key=settings.openai_api_key,
    )
