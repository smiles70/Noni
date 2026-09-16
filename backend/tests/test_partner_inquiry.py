"""Tests for POST /api/site/partner-inquiry."""

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
        "phone": "",
        "organization": "Sunrise Senior Living",
        "organization_type": "Senior living community",
        "role": "Director",
        "message": "We would like to learn about partnership.",
        "website": "",
    }
    base.update(overrides)
    return base


class TestPartnerInquiry:
    def test_valid_inquiry_accepted(self, client):
        with patch("backend.api.routes.site.email.send") as send:
            send.return_value = True
            res = client.post("/api/v1/site/partner-inquiry", json=_payload())
        assert res.status_code == 200
        body = res.json()
        assert body["status"] == "received"
        assert body["delivered"] is True
        send.assert_called_once()

    def test_honeypot_rejects_without_sending(self, client):
        with patch("backend.api.routes.site.email.send") as send:
            res = client.post(
                "/api/v1/site/partner-inquiry",
                json=_payload(website="spam.example"),
            )
        assert res.status_code == 200
        assert res.json()["delivered"] is False
        send.assert_not_called()

    def test_invalid_email_rejected(self, client):
        res = client.post(
            "/api/v1/site/partner-inquiry", json=_payload(email="not-an-email")
        )
        assert res.status_code == 422

    def test_missing_name_rejected(self, client):
        res = client.post("/api/v1/site/partner-inquiry", json=_payload(first_name=""))
        assert res.status_code == 422

    def test_missing_organization_rejected(self, client):
        res = client.post(
            "/api/v1/site/partner-inquiry", json=_payload(organization="")
        )
        assert res.status_code == 422

    def test_subject_and_body_include_organization(self, client):
        with patch("backend.api.routes.site.email.send") as send:
            client.post("/api/v1/site/partner-inquiry", json=_payload())
        args = send.call_args[0]
        assert "Sunrise Senior Living" in args[1]  # subject
        assert "maya@sunrise.example" in args[2]  # body
