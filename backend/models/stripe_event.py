"""Pydantic models for Stripe webhook event payloads.

Validates the JSON shape of incoming Stripe events at parse time
rather than accessing raw dict keys that may be missing on API drift.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class StripeEvent(BaseModel):
    """Top-level Stripe webhook event envelope."""

    id: str = Field(..., description="Stripe event ID (used for replay protection)")
    object: str = Field(default="event")
    api_version: str | None = None
    type: str = Field(
        ..., description="Stripe event type, e.g. 'invoice.payment_succeeded'"
    )
    data: dict[str, Any] = Field(..., description="Opaque event data object")

    @property
    def event_type(self) -> str:
        return self.type
