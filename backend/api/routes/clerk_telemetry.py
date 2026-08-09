"""Clerk telemetry endpoint for BetterStack integration.

Receives Clerk widget telemetry events from the frontend and forwards them
to BetterStack for monitoring and analysis.
"""

from typing import Any, Dict
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from backend.core.config import settings

router = APIRouter()


class ClerkTelemetryEvent(BaseModel):
    """Clerk telemetry event from frontend."""
    eventType: str
    timestamp: int
    metadata: Dict[str, Any] = {}


@router.post("/telemetry/clerk")
async def receive_clerk_telemetry(event: ClerkTelemetryEvent):
    """Receive Clerk widget telemetry and forward to BetterStack.
    
    This endpoint receives telemetry events from the frontend and forwards
    them to BetterStack for monitoring. If BetterStack is not configured,
    the events are logged but not sent.
    """
    # Log the event locally
    print(f"[Clerk Telemetry] {event.eventType}: {event.metadata}")
    
    # Forward to BetterStack if configured
    if settings.BETTERSTACK_API_KEY:
        try:
            import httpx
            
            betterstack_url = f"https://influxdb.betterstack.com/api/v2/write?org={settings.BETTERSTACK_SOURCE_NAME}"
            
            # Format as InfluxDB line protocol
            # BetterStack accepts InfluxDB line protocol for log ingestion
            line = f"clerk_telemetry,event_type={event.eventType} {event.metadata}"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    betterstack_url,
                    content=line,
                    headers={
                        "Authorization": f"Token {settings.BETTERSTACK_API_KEY}",
                        "Content-Type": "text/plain",
                    },
                )
                response.raise_for_status()
                
        except Exception as e:
            print(f"[Clerk Telemetry] Failed to send to BetterStack: {e}")
            # Don't fail the request - telemetry is best-effort
    else:
        print("[Clerk Telemetry] BetterStack not configured, skipping send")
    
    return {"status": "received"}