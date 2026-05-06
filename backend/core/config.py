"""Noni - System configuration via pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Noni"
    VERSION: str = "0.1.0"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/noni"
    SECRET_KEY: str = "development-secret-key-change-in-production"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )


settings = Settings()
