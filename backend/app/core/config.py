"""Application configuration via pydantic-settings."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(url: str) -> str:
    """Convert Neon/psycopg URLs to asyncpg-compatible SQLAlchemy URLs."""
    url = url.strip().strip('"').strip("'")
    if url.startswith("postgresql://"):
        url = f"postgresql+asyncpg://{url[len('postgresql://'):]}"
    elif url.startswith("postgres://"):
        url = f"postgresql+asyncpg://{url[len('postgres://'):]}"

    parsed = urlparse(url)
    if parsed.scheme != "postgresql+asyncpg":
        return url

    query_params: list[tuple[str, str]] = []
    for key, values in parse_qs(parsed.query, keep_blank_values=True).items():
        if key == "channel_binding":
            continue
        if key == "sslmode":
            if values[0] in ("require", "verify-ca", "verify-full"):
                query_params.append(("ssl", "require"))
            continue
        for value in values:
            query_params.append((key, value))

    return urlunparse(parsed._replace(query=urlencode(query_params)))


class Settings(BaseSettings):
    """Centralized environment-backed configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_api_key: SecretStr = Field(..., description="Shared API key for all clients")
    database_url: str = Field(
        ...,
        description="Async SQLAlchemy database URL (postgresql+asyncpg://...)",
    )

    groq_api_key: SecretStr = Field(..., description="Groq API key for chat completions")
    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq chat completion model",
    )
    groq_timeout_seconds: float = Field(default=60.0, ge=1.0)

    openrouter_api_key: SecretStr = Field(..., description="OpenRouter API key for embeddings")
    openrouter_embedding_model: str = Field(
        default="openai/text-embedding-3-large",
        description="OpenRouter embedding model (must match Pinecone index dimension)",
    )
    openrouter_timeout_seconds: float = Field(default=60.0, ge=1.0)

    pinecone_api_key: SecretStr = Field(..., description="Pinecone API key")
    pinecone_index_name: str = Field(default="docuchat")
    pinecone_timeout_seconds: float = Field(default=30.0, ge=1.0)

    max_pdf_size_bytes: int = Field(default=10 * 1024 * 1024, ge=1)
    max_documents_per_session: int = Field(default=3, ge=1)
    chunk_size: int = Field(default=1000, ge=100)
    chunk_overlap: int = Field(default=200, ge=0)
    retrieval_top_k: int = Field(default=5, ge=1)
    memory_message_limit: int = Field(default=10, ge=1)

    upload_dir: Path = Field(default=Path("uploads"))
    websocket_timeout_seconds: float = Field(default=300.0, ge=1.0)

    log_level: str = Field(default="INFO")
    environment: str = Field(default="development")

    cors_origins: list[str] = Field(default=["*"])

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url_field(cls, value: str) -> str:
        return normalize_database_url(value)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        stripped = value.strip()
        if stripped.startswith("["):
            parsed = json.loads(stripped)
            if not isinstance(parsed, list):
                raise ValueError("CORS_ORIGINS must be a JSON array")
            return [str(item) for item in parsed]
        return [origin.strip() for origin in value.split(",") if origin.strip()]

    @property
    def upload_dir_absolute(self) -> Path:
        return self.upload_dir.resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()
