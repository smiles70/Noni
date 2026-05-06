"""
Noni - Geragogy-grounded AI learning system for older adults.

All UI state transitions are governed by the Interface State Control
System (ISCS). Subsystems emit signals; the ISCS decides UI states.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI

from backend.core.config import settings
from backend.core.database import init_db
from backend.api.routes.curriculum import router as curriculum_router
from backend.api.routes.signals import router as signals_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A geragogy-grounded AI learning system for older adults",
    lifespan=lifespan,
)

app.include_router(curriculum_router, prefix="/api/curriculum", tags=["curriculum"])
app.include_router(signals_router, prefix="/api/signals", tags=["signals"])


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/")
async def root():
    return {"message": f"{settings.PROJECT_NAME} backend running", "version": settings.VERSION}
