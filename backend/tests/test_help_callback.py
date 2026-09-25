"""Help callback unit tests — learner "Call me" lane.

Covers the phone validator (US/CA only) and the Retell client
(capability-off + payload shape). The endpoint's honeypot/rate-limit
branches mirror the partner-inquiry conventions.
"""

from __future__ import annotations

import pytest

from backend.models.help_request import CallbackRequest
from backend.services import retell_calls


class TestPhoneValidation:
    def test_us_number_normalized_to_e164(self):
        r = CallbackRequest(phone="(555) 123-4567")
        assert r.phone == "+15551234567"

    def test_e164_passes_through(self):
        r = CallbackRequest(phone="+14155551234")
        assert r.phone == "+14155551234"

    def test_international_rejected(self):
        with pytest.raises(Exception):
            CallbackRequest(phone="+44 20 7946 0958")

    def test_garbage_rejected(self):
        with pytest.raises(Exception):
            CallbackRequest(phone="not a phone")


class TestRetellCallback:
    def test_unconfigured_returns_none(self, monkeypatch):
        monkeypatch.setattr(
            "backend.services.retell_calls.settings.RETELL_CALLBACK_AGENT_ID",
            "",
        )
        assert retell_calls.create_callback("+14155551234") is None

    def test_payload_shape(self, monkeypatch):
        calls: list[dict] = []

        class FakeResp:
            status_code = 201

            def json(self):
                return {"call_id": "call_abc"}

        def fake_post(url, json=None, headers=None, timeout=None):
            calls.append({"url": url, "json": json, "headers": headers})
            return FakeResp()

        monkeypatch.setattr(
            "backend.services.retell_calls.settings.RETELL_API_KEY", "k"
        )
        monkeypatch.setattr(
            "backend.services.retell_calls.settings.RETELL_CALLBACK_AGENT_ID",
            "agent_x",
        )
        monkeypatch.setattr("backend.services.retell_calls.httpx.post", fake_post)
        assert retell_calls.create_callback("+14155551234") == "call_abc"
        body = calls[0]["json"]
        assert body["to_number"] == "+14155551234"
        assert body["override_agent_id"] == "agent_x"
