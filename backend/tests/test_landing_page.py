"""Tests for the landing-page content and /api/landing/page route."""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.content.landing_page import LANDING_PAGE_CONTENT
from backend.models.landing_page import LandingPageContent


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


class TestContentIntegrity:
    def test_content_validates_against_schema(self):
        # Must round-trip through the Pydantic schema without error.
        LandingPageContent.model_validate(LANDING_PAGE_CONTENT)

    def test_all_expected_sections_present(self):
        expected = {
            "hero",
            "introduction",
            "what_noni_does",
            "how_it_feels",
            "trust_and_safety",
            "call_to_action",
            "closing",
        }
        assert set(LANDING_PAGE_CONTENT.keys()) == expected

    def test_ctas_have_label_and_note(self):
        cta = LANDING_PAGE_CONTENT["call_to_action"]
        for key in ("primary", "secondary"):
            assert "label" in cta[key] and cta[key]["label"].strip()
            assert "note" in cta[key] and cta[key]["note"].strip()

    def test_no_empty_strings(self):
        # Whitespace-only copy would be a regression.
        def walk(v):
            if isinstance(v, dict):
                for x in v.values():
                    walk(x)
            elif isinstance(v, list):
                for x in v:
                    walk(x)
            elif isinstance(v, str):
                assert v.strip(), "empty string in landing content"

        walk(LANDING_PAGE_CONTENT)


class TestLandingPageRoute:
    def test_get_landing_page_returns_200(self, client):
        r = client.get("/api/landing/page")
        assert r.status_code == 200

    def test_response_shape_matches_schema(self, client):
        r = client.get("/api/landing/page")
        LandingPageContent.model_validate(r.json())

    def test_primary_cta_label_matches_source(self, client):
        r = client.get("/api/landing/page")
        body = r.json()
        assert (
            body["call_to_action"]["primary"]["label"]
            == LANDING_PAGE_CONTENT["call_to_action"]["primary"]["label"]
        )


class TestStepsContractUnchanged:
    """Sprint 3 contract must still hold: display_* fields are None."""

    def test_display_fields_remain_none_on_all_steps(self, client):
        r = client.get("/api/landing/steps")
        for step in r.json()["steps"]:
            assert step["display_title"] is None
            assert step["display_body"] is None
            assert step["action_label"] is None
