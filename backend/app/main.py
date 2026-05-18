"""
Noni - Geragogy-grounded AI learning system for older adults.

All UI state transitions are governed by the Interface State Control
System (ISCS). Subsystems emit signals; the ISCS decides UI states.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.telemetry import TelemetryMiddleware
from backend.core.config import settings
from backend.core.database import run_migrations
from backend.api.routes.curriculum import router as curriculum_router
from backend.api.routes.signals import router as signals_router
from backend.api.routes.landing import router as landing_router
from backend.api.routes.telemetry_export import router as telemetry_export_router
from backend.api.routes.ui_envelope import router as ui_envelope_router
from backend.api.routes.auth import router as auth_router
from backend.api.routes.account import router as account_router
from backend.api.routes.billing import router as billing_router
from backend.api.routes.gifts import router as gifts_router


def _verify_crypto_dependency() -> None:
    """F10: fail loud at startup if PyJWT's RS256 support is unavailable.

    PyJWT 2.10.1 (our pin) does not raise an explicit ImportError when
    `cryptography` is missing; instead RS256 verification silently
    fails at first request, causing the auth-redirect loop G1 we hit
    on 2026-05-17. Force the failure at boot so ops sees it before
    any user does.
    """
    if settings.AUTH_PROVIDER.strip().lower() != "clerk":
        return
    try:
        import cryptography  # noqa: F401
        from jwt.algorithms import RSAAlgorithm  # noqa: F401
    except ImportError as exc:  # pragma: no cover - boot-time guard
        raise RuntimeError(
            "AUTH_PROVIDER=clerk requires `cryptography` for RS256 JWT "
            "verification. Install it: `pip install cryptography` (or "
            "`pip install 'pyjwt[crypto]'`). See docs/gotchas.md G1."
        ) from exc


@asynccontextmanager
async def lifespan(app: FastAPI):
    _verify_crypto_dependency()
    run_migrations()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A geragogy-grounded AI learning system for older adults",
    lifespan=lifespan,
)

# Dev CORS: explicit allowlist for local Vite dev server.
# Production deployments should override via reverse proxy / env-driven origins.
_cors_origins = (
    [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
    if settings.CORS_ORIGINS
    else ["http://localhost:5173", "http://127.0.0.1:5173"]
)
# Stage 0 telemetry (E10). Must run for every request to provide the
# observability baseline that Stage 1+ work is gated on. Added BEFORE
# CORSMiddleware so it observes the request even when CORS rejects it.
app.add_middleware(TelemetryMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    # ADR 0024: stateless Bearer auth. We do not read or write cookies
    # on cross-origin requests, so `allow_credentials=False` is correct
    # AND has a useful side effect: with credentials disabled the CORS
    # spec treats `allow_headers="*"` as a true wildcard (Clerk's SDK
    # sends `x-client-version` and friends without any explicit
    # allowlist). With credentials enabled, the wildcard does not match
    # any header per the Fetch spec.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(curriculum_router, prefix="/api/curriculum", tags=["curriculum"])
app.include_router(signals_router, prefix="/api/signals", tags=["signals"])
app.include_router(landing_router, prefix="/api/landing", tags=["landing"])
app.include_router(telemetry_export_router, prefix="/api/telemetry", tags=["telemetry"])
app.include_router(ui_envelope_router, prefix="/api/ui-envelope", tags=["ui-envelope"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(account_router, prefix="/me", tags=["account"])
app.include_router(billing_router, prefix="/api/billing", tags=["billing"])
app.include_router(gifts_router, prefix="/api/gifts", tags=["gifts"])


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/")
async def root():
    return {
        "message": f"{settings.PROJECT_NAME} backend running",
        "version": settings.VERSION,
    }
