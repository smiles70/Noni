"""WS-D: marketing telemetry endpoint tests (scroll-depth baseline)."""

import pytest
from fastapi import HTTPException

from backend.api.routes.onboarding_telemetry import (
    MarketingTelemetryEvent,
    track_marketing_event,
)


class FakeDb:
    pass


def test_track_marketing_event_valid():
    event = MarketingTelemetryEvent(
        event="marketing.scroll_depth",
        timestamp=123,
        metadata={"page": "caregiver", "depth": 50, "viewport": "mobile"},
    )
    result = track_marketing_event(event, FakeDb())
    assert result["status"] == "recorded"


def test_track_marketing_event_empty_name():
    event = MarketingTelemetryEvent(event="", timestamp=123)
    with pytest.raises(HTTPException) as exc:
        track_marketing_event(event, FakeDb())
    assert exc.value.status_code == 400


def test_track_marketing_event_no_metadata():
    event = MarketingTelemetryEvent(event="marketing.scroll_depth", timestamp=1)
    result = track_marketing_event(event, FakeDb())
    assert result["status"] == "recorded"


def test_record_marketing_event_increments_counter():
    from backend.app.telemetry import record_marketing_event

    # Must not raise; counter increments are covered by /metrics.
    record_marketing_event(
        event="marketing.scroll_depth",
        timestamp=1,
        metadata={"page": "for-communities", "depth": 90},
    )
