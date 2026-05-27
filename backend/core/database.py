"""Database engine and session management.

Per ARCHITECTURE.md rule 9 (Auditability): all persistent state
flows through this single configured engine.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from backend.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_reset_on_return="rollback",
    # Sprint 23 M2: fail fast on slow connections and runaway queries
    connect_args={
        "connect_timeout": 10,
        "options": "-c statement_timeout=30000",  # 30 seconds
    },
)
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


def run_migrations() -> None:
    """Apply Alembic migrations on startup.

    Replaces the previous Base.metadata.create_all() approach.
    See ADR 0005 for rationale.

    Note: Alembic operates via a synchronous DBAPI driver (psycopg2)
    because DDL operations (CREATE TABLE, ALTER COLUMN, etc.) are
    inherently synchronous I/O.  SQLAlchemy's async extension does
    not support DDL execution, and Alembic's own cookbook confirms
    that migrations should run through a sync engine even when the
    application uses asyncpg for request handling.  Do NOT switch
    this to create_async_engine() or asyncpg — migrations will fail.
    Ref: https://alembic.sqlalchemy.org/en/latest/cookbook.html#using-asyncio-with-alembic
    """
    from alembic import command
    from alembic.config import Config

    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    command.upgrade(cfg, "head")
