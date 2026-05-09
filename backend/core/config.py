from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Neon usually provides a DATABASE_URL in the form:
    postgresql://user:password@host/database?sslmode=require
    The database session module normalizes that URL for SQLAlchemy's asyncpg
    driver, so this setting can use the Neon value directly.
    """

    database_url: str = Field(..., alias="DATABASE_URL")
    app_name: str = Field(default="FloatChat AI Backend", alias="APP_NAME")
    environment: str = Field(default="local", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    auto_create_schema: bool = Field(default=True, alias="AUTO_CREATE_SCHEMA")

    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama3-70b-8192", alias="GROQ_MODEL")
    groq_temperature: float = Field(default=0.2, alias="GROQ_TEMPERATURE")
    groq_max_retries: int = Field(default=2, alias="GROQ_MAX_RETRIES")
    groq_timeout_seconds: int = Field(default=30, alias="GROQ_TIMEOUT_SECONDS")

    sql_allowlist_tables: str = Field(
        default="floats,profiles,measurements,active_floats_summary",
        alias="SQL_ALLOWLIST_TABLES",
    )
    sql_max_rows: int = Field(default=500, alias="SQL_MAX_ROWS")
    sql_max_retries: int = Field(default=1, alias="SQL_MAX_RETRIES")
    sql_max_cost: int = Field(default=1000, alias="SQL_MAX_COST")

    measurement_ttl_days: int = Field(default=7, alias="MEASUREMENT_TTL_DAYS")

    qstash_current_signing_key: str | None = Field(
        default=None, alias="QSTASH_CURRENT_SIGNING_KEY"
    )
    qstash_next_signing_key: str | None = Field(
        default=None, alias="QSTASH_NEXT_SIGNING_KEY"
    )
    qstash_target_url: str | None = Field(default=None, alias="QSTASH_TARGET_URL")

    upstash_redis_rest_url: str | None = Field(
        default=None, alias="UPSTASH_REDIS_REST_URL"
    )
    upstash_redis_rest_token: str | None = Field(
        default=None, alias="UPSTASH_REDIS_REST_TOKEN"
    )
    _root_env_path = Path(__file__).resolve().parents[2] / ".env"

    model_config = SettingsConfigDict(
        env_file=_root_env_path,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached settings so env parsing happens once per process."""

    return Settings()
