"""Noni - System configuration via pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Noni"
    VERSION: str = "0.1.0"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/noni"
    DATABASE_URL_DIRECT: str = (
        ""  # non-pooled URL for migrations (defaults to DATABASE_URL)
    )
    SECRET_KEY: str = "development-secret-key-change-in-production"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Session / cookie (ADR 0023). Rotate quarterly minimum.
    SESSION_SECRET: str = "dev-session-secret-change-in-production"
    SESSION_COOKIE_NAME: str = "noni_session"
    SESSION_TTL_DAYS: int = 30

    # Identity provider: 'mock' for dev/tests, 'supabase' in production.
    AUTH_PROVIDER: str = "mock"
    SUPABASE_URL: str = ""
    SUPABASE_JWT_SECRET: str = ""
    SUPABASE_JWT_AUDIENCE: str = "authenticated"
    SUPABASE_JWT_ISSUER: str = ""

    # Deletion grace period.
    DELETION_GRACE_PERIOD_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )


settings = Settings()
