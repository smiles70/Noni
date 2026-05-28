"""Enterprise Test Suite ET-1 — API Contract Validation.

Validates that every public API endpoint returns the documented wire shape.
All tests run against the versioned `/api/v1/` surface (not legacy redirects).
"""

from __future__ import annotations

from fastapi.testclient import TestClient

PAID_BUNDLE_CODE = "modules_4_5"


# ---------------------------------------------------------------------------
# Health & Discovery
# ---------------------------------------------------------------------------


def test_health_returns_200_with_expected_shape(client: TestClient):
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "healthy"
    assert "version" in body
    assert "environment" in body


def test_openapi_schema_exists_and_has_paths(client: TestClient):
    res = client.get("/openapi.json")
    assert res.status_code == 200
    schema = res.json()
    assert "paths" in schema
    assert isinstance(schema["paths"], dict)
    assert len(schema["paths"]) > 0
    # Versioned surface should be present
    assert any(p.startswith("/api/v1/") for p in schema["paths"])


# ---------------------------------------------------------------------------
# Curriculum (Versioned Paths)
# ---------------------------------------------------------------------------


def test_curriculum_units_list_returns_catalog(client: TestClient):
    res = client.get("/api/v1/curriculum/units")
    assert res.status_code == 200
    body = res.json()
    assert "units" in body
    assert isinstance(body["units"], list)
    assert len(body["units"]) > 0
    unit = body["units"][0]
    assert "id" in unit
    assert "title" in unit
    assert "max_complexity" in unit


def test_curriculum_menu_returns_modules_and_bridge_units(client: TestClient):
    res = client.get("/api/v1/curriculum/menu")
    assert res.status_code == 200
    body = res.json()
    assert "modules" in body
    assert "bridge_units" in body
    assert isinstance(body["modules"], list)
    assert len(body["modules"]) > 0
    module = body["modules"][0]
    assert "id" in module
    assert "title" in module
    assert "units" in module


def test_curriculum_unit_page_returns_iscs_approved(client: TestClient):
    # Free track unit (unit-3 is in the catalog)
    res = client.get("/api/v1/curriculum/units/unit-3")
    assert res.status_code == 200
    body = res.json()
    assert "unit_id" in body
    assert "unit_title" in body
    assert "ui_state" in body
    assert "stability" in body


def test_curriculum_lesson_returns_full_page_list(client: TestClient):
    res = client.get("/api/v1/curriculum/units/unit-3/lesson")
    assert res.status_code == 200
    body = res.json()
    assert "unit_id" in body
    assert "unit_title" in body
    assert "pages" in body
    assert isinstance(body["pages"], list)
    assert len(body["pages"]) > 0
    page = body["pages"][0]
    assert "id" in page
    assert "title" in page


# ---------------------------------------------------------------------------
# UI State Envelope (ADR 0019 Contract)
# ---------------------------------------------------------------------------


def test_ui_envelope_landing_page_has_full_contract(client: TestClient):
    res = client.get("/api/v1/ui-envelope/landing.page")
    assert res.status_code == 200
    data = res.json()
    assert data["state_id"] == "landing.page"
    assert "authorized_components" in data
    assert isinstance(data["authorized_components"], list)
    assert len(data["authorized_components"]) > 0
    assert "interaction_limits" in data
    assert "layout_constraints" in data
    assert "transition_permissions" in data


def test_ui_envelope_curriculum_unit_has_full_contract(client: TestClient):
    res = client.get("/api/v1/ui-envelope/curriculum.unit")
    assert res.status_code == 200
    data = res.json()
    assert data["state_id"] == "curriculum.unit"
    assert "authorized_components" in data
    assert "interaction_limits" in data


def test_ui_envelope_undefined_state_returns_404(client: TestClient):
    res = client.get("/api/v1/ui-envelope/undefined.state.xyz")
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# Auth (Redesign Endpoints — Versioned)
# ---------------------------------------------------------------------------


def test_auth_config_public_no_auth_required(client: TestClient):
    res = client.get("/api/v1/auth/config")
    assert res.status_code == 200
    body = res.json()
    assert "provider" in body
    assert "version" in body


def test_auth_session_with_valid_token_materializes_account(
    client: TestClient, auth_headers
):
    headers = auth_headers("et-contract@example.com")
    res = client.get("/api/v1/auth/session", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert "subject" in body
    assert "materialized" in body
    # First call: unmaterialized (row doesn't exist yet)
    if body["materialized"] is False:
        # Materialize it
        init_res = client.post("/api/v1/auth/session/init", headers=headers)
        assert init_res.status_code == 200
        # Now should be materialized
        res2 = client.get("/api/v1/auth/session", headers=headers)
        assert res2.status_code == 200
        body = res2.json()
    assert body["materialized"] is True
    assert "account_id" in body
    assert "email" in body


def test_auth_session_init_idempotent(client: TestClient, auth_headers):
    headers = auth_headers("et-idempotent@example.com")
    r1 = client.post("/api/v1/auth/session/init", headers=headers)
    assert r1.status_code == 200
    id1 = r1.json()["account_id"]
    r2 = client.post("/api/v1/auth/session/init", headers=headers)
    assert r2.status_code == 200
    id2 = r2.json()["account_id"]
    assert id1 == id2


# ---------------------------------------------------------------------------
# Billing (Versioned)
# ---------------------------------------------------------------------------


def test_billing_health_returns_provider_info(client: TestClient):
    res = client.get("/api/v1/billing/health")
    assert res.status_code == 200
    body = res.json()
    assert "provider" in body
    assert "stripe_mode" in body
