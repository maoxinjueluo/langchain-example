from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    env: str = Field(default="dev", validation_alias="ENV")
    testing: bool = Field(default=False, validation_alias="TESTING")

    app_base_url: str = Field(default="http://localhost:8000", validation_alias="APP_BASE_URL")

    database_url: str = Field(default="sqlite+aiosqlite:///db/app.db", validation_alias="DATABASE_URL")

    secret_key: str = Field(default="change-me", validation_alias="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    access_token_expires_minutes: int = Field(
        default=60,
        validation_alias="ACCESS_TOKEN_EXPIRES_MINUTES",
        ge=5,
        le=24 * 60,
    )
    remember_me_days: int = Field(default=14, validation_alias="REMEMBER_ME_DAYS", ge=1, le=90)

    smtp_host: Optional[str] = Field(default=None, validation_alias="SMTP_HOST")
    smtp_port: int = Field(default=587, validation_alias="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, validation_alias="SMTP_USER")
    smtp_password: Optional[str] = Field(default=None, validation_alias="SMTP_PASSWORD")
    mail_from: str = Field(default="no-reply@example.com", validation_alias="MAIL_FROM")

    upload_dir: str = Field(default=str(Path("db/uploads").resolve()), validation_alias="UPLOAD_DIR")
    max_upload_mb: int = Field(default=50, validation_alias="MAX_UPLOAD_MB", ge=1, le=200)
    chroma_dir: str = Field(default=str(Path("db/chroma").resolve()), validation_alias="CHROMA_DIR")
    retrieval_top_k: int = Field(default=5, validation_alias="RETRIEVAL_TOP_K", ge=1, le=20)
    confidence_threshold: float = Field(default=0.35, validation_alias="CONFIDENCE_THRESHOLD", ge=0.0, le=1.0)

    openai_api_key: Optional[str] = Field(
        default="sk-c59f00de440942aeb0e45494f575d582", validation_alias="OPENAI_API_KEY"
    )
    openai_chat_model: str = Field(default="qwen3-max", validation_alias="OPENAI_CHAT_MODEL")
    openai_embeddings_model: str = Field(
        default="text-embedding-3-small",
        validation_alias="OPENAI_EMBEDDINGS_MODEL",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
