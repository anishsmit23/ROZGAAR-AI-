from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    public_api_url: str = "http://127.0.0.1:8000"
    cors_extra_origins: str = ""

    database_url: str
    redis_url: str
    chroma_url: str

    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str = "raw-html"

    celery_broker_url: str
    celery_result_backend: str

    jwt_private_key: str
    jwt_public_key: str
    jwt_access_token_expire_minutes: int = 60
    reset_password_secret: str = "reset-password-secret"
    verification_secret: str = "verification-secret"

    groq_api_key: str | None = None
    openai_api_key: str | None = None
    groq_base_url: str | None = None
    llm_model: str | None = None
    llm_temperature: float = 0.2


@lru_cache
def get_settings() -> Settings:
    return Settings()
