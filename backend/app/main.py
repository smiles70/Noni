"""
Noni - Geragogy-grounded AI learning system for older adults.

All UI state transitions are governed by the Interface State Control
System (ISCS). Subsystems emit signals; the ISCS decides UI states.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@asynccontextmanager
async def lifespan(app: FastAPI):
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
