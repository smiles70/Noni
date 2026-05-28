"""Enterprise Test Suite ET-1 — Security Validation.

Validates security headers, CORS, auth failure paths, and legacy redirect
behaviour on the versioned API surface.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

FRONTEND_ORIGIN = "http://localhost:5173"


# ---------------------------------------------------------------------------
# Security Headers
# ---------------------------------------------------------------------------


def test_security_headers_present_on_health(client: TestClient):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-XSS-Protection") == "1; mode=block"
    assert res.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "Content-Security-Policy" in res.headers


def test_security_headers_present_on_versioned_endpoint(client: TestClient):
    res = client.get("/api/v1/curriculum/units")
    assert res.status_code == 200
    assert res.headers.get("X-Frame-Options") == "DENY"


def test_hsts_not_present_in_non_production(client: TestClient):
    res = client.get("/health")
    assert res.status_code == 200
    # HSTS is only injected when ENVIRONMENT == "production"
    assert "Strict-Transport-Security" not in res.headers


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------


def test_cors_preflight_returns_allow_origin(client: TestClient):
    res = client.options(
        "/api/v1/curriculum/units",
        headers={
            "Origin": FRONTEND_ORIGIN,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert res.status_code == 200
    assert "access-control-allow-origin" in res.headers
    assert "access-control-allow-methods" in res.headers


def test_cors_get_returns_allow_origin(client: TestClient):
    res = client.get(
        "/api/v1/curriculum/units",
        headers={"Origin": FRONTEND_ORIGIN},
    )
    assert res.status_code == 200
    assert "access-control-allow-origin" in res.headers


def test_cors_without_origin_does_not_leak_allow_origin(client: TestClient):
    res = client.get("/api/v1/curriculum/units")
    assert res.status_code == 200
    # No Origin header -> no CORS headers (FastAPI CORS middleware behaviour)
    assert "access-control-allow-origin" not in res.headers


# ---------------------------------------------------------------------------
# Auth Failure Paths (Versioned)
# ---------------------------------------------------------------------------


def test_auth_session_without_header_returns_401(client: TestClient):
    res = client.get("/api/v1/auth/session")
    assert res.status_code == 401
    body = res.json()
    assert "error" in body
    assert "code" in body["error"]


def test_auth_session_with_invalid_token_returns_401(client: TestClient):
    res = client.get(
        "/api/v1/auth/session",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert res.status_code == 401
    body = res.json()
    assert "error" in body


def test_auth_session_with_wrong_scheme_returns_401(client: TestClient):
    res = client.get(
        "/api/v1/auth/session",
        headers={"Authorization": "Basic mock:user@example.com"},
    )
    assert res.status_code == 401


def test_protected_billing_checkout_without_auth_returns_401(client: TestClient):
    res = client.post(
        "/api/v1/billing/checkout",
        json={"product_code": "modules_4_5", "is_gift": False},
    )
    assert res.status_code == 401


# ---------------------------------------------------------------------------
# Legacy Redirects
# ---------------------------------------------------------------------------


def test_legacy_curriculum_redirects_to_v1_with_302(client: TestClient):
    res = client.get("/api/curriculum/units", follow_redirects=False)
    assert res.status_code == 302
    assert "/api/v1/curriculum" in res.headers["location"]
    assert res.headers.get("Deprecation") == "true"
    assert "Sunset" in res.headers


def test_legacy_auth_redirects_to_v1_with_302(client: TestClient):
    res = client.get("/auth/whoami", follow_redirects=False)
    assert res.status_code == 302
    assert "/api/v1/auth" in res.headers["location"]
