"""Tests for the site-chrome /api/site/footer route and content."""

import re
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.content.site_chrome import SITE_FOOTER_CONTENT
from backend.models.site_chrome import SiteFooterContent


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


class TestContentIntegrity:
    def test_content_validates_against_schema(self):
        payload = dict(SITE_FOOTER_CONTENT)
        payload["copyright"] = "© 2026 mynaani. All rights reserved."
        SiteFooterContent.model_validate(payload)

    def test_all_expected_sections_present(self):
        expected = {
            "tagline",
            "nav_links",
            "legal_links",
            "mini_links",
            "brand_label",
        }
        assert set(SITE_FOOTER_CONTENT.keys()) == expected

    def test_links_point_to_internal_routes(self):
        for group in ("nav_links", "legal_links", "mini_links"):
            for link in SITE_FOOTER_CONTENT[group]:
                assert link["href"].startswith("/")
                assert link["label"].strip()

    def test_privacy_link_present(self):
        # CCPA §7011(d): conspicuous link using the word "privacy".
        hrefs = {
            link["href"] for link in SITE_FOOTER_CONTENT["legal_links"]
        }
        assert "/privacy" in hrefs
        labels = {
            link["label"].lower()
            for link in SITE_FOOTER_CONTENT["legal_links"]
        }
        assert any("privacy" in label for label in labels)


class TestFooterRoute:
    def test_get_footer_returns_typed_content(self, client):
        res = client.get("/api/v1/site/footer")
        assert res.status_code == 200
        body = res.json()
        SiteFooterContent.model_validate(body)
        assert body["tagline"]
        assert len(body["nav_links"]) >= 4
        assert len(body["mini_links"]) >= 2

    def test_copyright_has_current_year(self, client):
        res = client.get("/api/v1/site/footer")
        year = datetime.now(timezone.utc).year
        assert str(year) in res.json()["copyright"]

    def test_legacy_prefix_redirects(self, client):
        res = client.get("/api/site/footer", follow_redirects=False)
        assert res.status_code in (301, 302, 307, 308)
        assert re.search(r"/api/v1/site/footer", res.headers["location"])

    def test_cacheable(self, client):
        res = client.get("/api/v1/site/footer")
        assert "public" in res.headers.get("cache-control", "")
