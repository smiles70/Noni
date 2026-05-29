"""Noni - System configuration via pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Noni"
    VERSION: str = "0.1.0"
    DATABASE_URL: str = ""
    DATABASE_URL_DIRECT: str = (
        ""  # non-pooled URL for migrations (defaults to DATABASE_URL)
    )
    SECRET_KEY: str = ""
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Session / cookie (ADR 0023). Rotate quarterly minimum.
    SESSION_SECRET: str = ""
    SESSION_COOKIE_NAME: str = "noni_session"
    SESSION_TTL_DAYS: int = 30

    # Identity provider. "mock" (dev/tests, MockAuthProvider) or "clerk"
    # (production, ClerkAuthProvider with RS256 + JWKS). The legacy
    # "supabase" value is rejected by `get_auth_provider()` — Supabase
    # is the Postgres database, not an identity provider.
    AUTH_PROVIDER: str = "mock"
    # The browser app origin we redirect users back to after auth. Used
    # by the Clerk integration's post-signin redirect and by any future
    # backend-initiated redirect. Defaults to the local Compose stack.
    FRONTEND_URL: str = "http://localhost:8080"

    # Clerk integration (ADR 0024). Required when AUTH_PROVIDER=clerk.
    # JWKS_URL is the public key endpoint Clerk exposes per instance,
    # of the form https://<frontend-api>.clerk.accounts.dev/.well-known/jwks.json
    # (dev) or https://clerk.<your-domain>.com/.well-known/jwks.json (prod).
    # ISSUER must match the `iss` claim on Clerk-issued JWTs; usually the
    # same host without /.well-known/jwks.json.
    CLERK_JWKS_URL: str = ""
    CLERK_ISSUER: str = ""
    # Optional: secret key for Clerk Backend SDK calls (revocations, user
    # lookups). Not required for JWT verification, but reserved here so
    # future server-side admin endpoints can pick it up without a config
    # migration.
    CLERK_SECRET_KEY: str = ""

    # Payment provider: 'mock' for dev/tests, 'stripe' in production.
    PAYMENT_PROVIDER: str = "mock"
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_ID_MODULES_4_5: str = ""
    STRIPE_SUCCESS_URL: str = "http://localhost:5173/purchase/success"
    STRIPE_CANCEL_URL: str = "http://localhost:5173/purchase/cancel"

    # Deletion grace period.
    DELETION_GRACE_PERIOD_DAYS: int = 7

    # Admin account UUIDs (comma-separated) for telemetry export gating.
    ADMIN_ACCOUNT_IDS: str = ""

    # Sprint 27 #92: log sampling rate (0.0–1.0) for info-level request logs.
    # Errors and warnings are always logged at 100%.
    LOG_SAMPLING_RATE: float = 1.0

    # CORS allowlist (comma-separated origins). Empty -> dev fallback in main.py.
    CORS_ORIGINS: str = ""

    # DB connection pool (ADR 0024 operational policy).
    # Tune these to your Postgres max_connections. Supabase free=30, pro=60.
    # Each Gunicorn worker gets its own pool, so total conn = workers * (pool_size + max_overflow).
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 10
    DB_POOL_RECYCLE: int = 3600

    # Gunicorn worker count. Override per-machine via Fly env or docker-compose.
    # Formula: (2 * CPU cores) + 1. shared-cpu-1x (1 core) -> 3; performance-2x (2 core) -> 5.
    WEB_CONCURRENCY: int = 1

    # Redis-backed rate limiting and Celery broker. Empty keeps local/test
    # environments on the Postgres fallback limiter.
    REDIS_URL: str = ""

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )


settings = Settings()


def validate_settings() -> None:
    """Runtime validation only (NOT import-time) prevents breaking pytest, CLI, migrations."""
    if not settings.DATABASE_URL:
        raise RuntimeError("DATABASE_URL must be set via environment variables")

    # Sprint '2nd Safe Yellow' P1: non-breaking secret rotation visibility.
    from backend.core.secret_rotation import warn_if_secret_old

    for name in ("SECRET_KEY", "SESSION_SECRET", "CLERK_SECRET_KEY", "STRIPE_SECRET_KEY"):
        warn_if_secret_old(name, max_age_sec=60 * 60 * 24 * 90)
