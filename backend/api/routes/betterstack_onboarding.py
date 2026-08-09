"""BetterStack integration for onboarding telemetry.

EPIC-002 Phase 4: BetterStack monitoring integration for onboarding flow.

This module integrates with BetterStack for comprehensive monitoring of
the onboarding flow, including error tracking, performance metrics, and
user journey analytics.
"""

from __future__ import annotations

import logging
import os
from typing import Optional
from fastapi import Header

from backend.core.config import settings

logger = logging.getLogger("noni.betterstack_onboarding")


class BetterStackOnboardingClient:
    """Client for sending onboarding telemetry to BetterStack."""

    def __init__(self):
        self.api_key = getattr(settings, "BETTERSTACK_API_KEY", None)
        self.source_name = getattr(settings, "BETTERSTACK_ONBOARDING_SOURCE_NAME", "noni-onboarding")
        self.enabled = bool(self.api_key)

    def send_event(self, event_data: dict) -> bool:
        """Send onboarding event to BetterStack.

        Args:
            event_data: Event data to send

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            # Silently skip if BetterStack is not configured
            return False

        try:
            import httpx

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "source": self.source_name,
                "event": event_data,
            }

            response = httpx.post(
                "https://api.betterstack.com/v1/logs",
                headers=headers,
                json=payload,
                timeout=5.0,
            )

            if response.status_code == 200:
                return True
            else:
                logger.warning(f"BetterStack API error: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error sending to BetterStack: {e}")
            return False


# Global client instance
_betterstack_client: Optional[BetterStackOnboardingClient] = None


def get_betterstack_client() -> BetterStackOnboardingClient:
    """Get or create the BetterStack client instance."""
    global _betterstack_client
    if _betterstack_client is None:
        _betterstack_client = BetterStackOnboardingClient()
    return _betterstack_client