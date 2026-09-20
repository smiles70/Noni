"""Tests for POST /api/v1/site/contact-inquiry (the /contact form)."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _payload(**overrides):
    base = {
        "first_name": "Maya",
        "last_name": "Rivera",
        "email": "maya@sunrise.example",
        "phone": "+1 555 0100",
        "website": "",
    }
    base.update(overrides)
    return base


class TestContactInquiry:
    def test_valid_inquiry_accepted(self, client):
        with patch("backend.api.routes.site.email.send") as send:
            send.return_value = True
            res = client.post("/api/v1/site/contact-inquiry", json=_payload())
        assert res.status_code == 200
        body = res.json()
        assert body["status"] == "received"
        assert body["delivered"] is True
        send.assert_called_once()

    def test_honeypot_rejects_without_sending(self, client):
        with patch("backend.api.routes.site.email.send") as send:
            res = client.post(
                "/api/v1/site/contact-inquiry",
                json=_payload(website="spam.example"),
            )
        assert res.status_code == 200
        assert res.json()["delivered"] is False
        send.assert_not_called()

    def test_invalid_email_rejected(self, client):
        res = client.post(
            "/api/v1/site/contact-inquiry", json=_payload(email="not-an-email")
        )
        assert res.status_code == 422

    def test_missing_name_rejected(self, client):
        res = client.post("/api/v1/site/contact-inquiry", json=_payload(first_name=""))
        assert res.status_code == 422

    def test_goes_to_help_inbox(self, client):
        with patch("backend.api.routes.site.email.send") as send:
            client.post("/api/v1/site/contact-inquiry", json=_payload())
        args = send.call_args[0]
        assert args[0] == "help@mynaani.com"
        assert "Maya Rivera" in args[1]  # subject
        assert "maya@sunrise.example" in args[2]  # body
