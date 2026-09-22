"""Settings from the environment. Every variable is documented in .env.example."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PAPERGLASS_", extra="ignore")

    env: str = Field(default="development", alias="APP_ENV")
    database_url: str = Field(default="sqlite+pysqlite:///./paperglass-dev.sqlite3")
    session_secret: str = Field(default="dev-only-change-me-dev-only-change-me")
    cors_origins: str = Field(default="http://localhost:5173,http://localhost:3000")
    retention_days: int = Field(default=7, ge=1)
    purge_interval_minutes: int = Field(default=60, ge=1)
    max_upload_mb: int = Field(default=25, ge=1)
    metrics_token: str | None = None
    log_level: str = "info"

    @property
    def cors_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def validate_for_startup(self) -> None:
        """Refuse to start a non-development environment with the placeholder secret."""
        if self.env != "development" and (
            len(self.session_secret) < 32 or self.session_secret.startswith("dev-only")
        ):
            msg = "PAPERGLASS_SESSION_SECRET must be a real secret of at least 32 characters"
            raise RuntimeError(msg)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
