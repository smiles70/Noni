"""
Noni - Geragogy-grounded AI learning system for older adults.
Main application entry point.

All UI state transitions are governed by the Interface State Control
System (ISCS). Subsystems emit signals; the ISCS decides UI states.
"""
from fastapi import FastAPI

from backend.api.routes.curriculum import router as curriculum_router
from backend.api.routes.signals import router as signals_router


VERSION = "0.1.0"

app = FastAPI(
    title="Noni",
    version=VERSION,
    description="A geragogy-grounded AI learning system for older adults",
)

app.include_router(curriculum_router, prefix="/api/curriculum", tags=["curriculum"])
app.include_router(signals_router, prefix="/api/signals", tags=["signals"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": VERSION}


@app.get("/")
async def root():
    return {"message": "Geragogy AI Tutor Backend Running", "version": VERSION}
