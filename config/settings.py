"""Runtime settings and shared dependency factories."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from langchain_openai import ChatOpenAI
from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from exceptions import ConfigurationError

# Groq exposes an OpenAI-compatible Chat Completions API.
DEFAULT_GROQ_BASE_URL = "https://api.groq.com/openai/v1"


class Settings(BaseSettings):
    """Environment-backed application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_base_url: str = Field(default=DEFAULT_GROQ_BASE_URL, alias="GROQ_BASE_URL")
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
    # Optional: Streamlit and other frontends use this to reach the API (e.g. docker host name).
    public_api_url: str = Field(default="http://127.0.0.1:8000", alias="PUBLIC_API_URL")
    # Comma-separated extra CORS origins (e.g. https://xxx.streamlit.app)
    cors_extra_origins: str = Field(default="", alias="CORS_EXTRA_ORIGINS")

    # Groq model id — see https://console.groq.com/docs/models
    llm_model: str = Field(default="llama-3.3-70b-versatile", alias="LLM_MODEL")
    llm_temperature: float = Field(default=0.2, alias="LLM_TEMPERATURE")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings and ensure data directories exist."""

    settings = Settings()
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    settings.chroma_path.mkdir(parents=True, exist_ok=True)
    return settings


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    """Chat LLM via Groq (OpenAI-compatible API)."""

    settings = get_settings()
    if not settings.groq_api_key:
        raise ConfigurationError("GROQ_API_KEY is missing in environment configuration.")

    base = (settings.groq_base_url or DEFAULT_GROQ_BASE_URL).rstrip("/")
    logger.debug("Initializing Groq ChatOpenAI model: {} @ {}", settings.llm_model, base)
    return ChatOpenAI(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        api_key=settings.groq_api_key,
        base_url=base,
    )
