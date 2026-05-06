"""
Noni - System configuration.
Environment-based configuration management.
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    PROJECT_NAME: str = "Noni"
    VERSION: str = "0.1.0"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/noni"
    
    # Security
    SECRET_KEY: str = "development-secret-key-change-in-production"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
