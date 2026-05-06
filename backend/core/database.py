"""Database engine and session management.

Per ARCHITECTURE.md rule 9 (Auditability): all persistent state
flows through this single configured engine.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator

from backend.core.config import settings


engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yields a request-scoped session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables registered on Base. Idempotent."""
    # Import models to register them with Base.metadata
    from backend.models.telemetry import TelemetryEvent  # noqa: F401
    Base.metadata.create_all(bind=engine)
