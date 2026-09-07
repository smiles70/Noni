"""AC-1: admin console access control.

The console is staff-only by design — same guard family as the org
dashboard tests. whoami-check is the soft probe for the frontend gate.
"""

from __future__ import annotations


def test_whoami_requires_session(client):
    r = client.get("/api/v1/admin/whoami")
    assert r.status_code == 401
    assert r.json()["detail"]["envelope_id"] == "auth.signed_out"


def test_whoami_check_is_soft(client):
    r = client.get("/api/v1/admin/whoami-check")
    assert r.status_code == 200
    assert r.json() == {"staff": False}


def test_orgs_rejects_non_staff(authenticated_client):
    r = authenticated_client.get("/api/v1/admin/orgs?q=oak")
    assert r.status_code == 403


def test_orgs_requires_min_query(authenticated_client):
    r = authenticated_client.get("/api/v1/admin/orgs?q=ab")
    assert r.status_code in (403, 422)


def test_flags_rejects_non_staff(authenticated_client):
    r = authenticated_client.get("/api/v1/admin/flags")
    assert r.status_code == 403


# ---------- ADMIN-LOGIN-001: staff console username+password login ----------


def _set_login_env(monkeypatch):
    import hashlib
    from backend.core.config import settings

    monkeypatch.setattr(settings, "ADMIN_CONSOLE_USERS", "kim,steven")
    monkeypatch.setattr(
        settings,
        "ADMIN_CONSOLE_PASSWORD_SHA256",
        hashlib.sha256(b"test-pass-123").hexdigest(),
    )
    monkeypatch.setattr(settings, "SESSION_SECRET", "test-session-secret")


def test_login_rejects_bad_credentials(client, monkeypatch):
    _set_login_env(monkeypatch)
    r = client.post(
        "/api/v1/admin/login",
        json={"username": "kim", "password": "wrong"},
    )
    assert r.status_code == 401
    assert r.json()["detail"]["envelope_id"] == "admin.invalid_credentials"


def test_login_fails_closed_without_config(client, monkeypatch):
    from backend.core.config import settings

    monkeypatch.setattr(settings, "ADMIN_CONSOLE_PASSWORD_SHA256", "")
    r = client.post(
        "/api/v1/admin/login",
        json={"username": "kim", "password": "test-pass-123"},
    )
    assert r.status_code == 401


def test_login_success_grants_staff_access(client, monkeypatch):
    _set_login_env(monkeypatch)
    # username is case-insensitive per spec
    r = client.post(
        "/api/v1/admin/login",
        json={"username": "KIM", "password": "test-pass-123"},
    )
    assert r.status_code == 200
    token = r.json()["token"]
    assert token.startswith("staff.")

    r = client.get("/api/v1/admin/whoami", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json() == {"staff": True}

    r = client.get(
        "/api/v1/admin/whoami-check",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json() == {"staff": True}


def test_staff_token_tampered_rejected(client, monkeypatch):
    _set_login_env(monkeypatch)
    r = client.post(
        "/api/v1/admin/login",
        json={"username": "steven", "password": "test-pass-123"},
    )
    token = r.json()["token"]
    forged = token[:-1] + ("A" if token[-1] != "A" else "B")
    r = client.get(
        "/api/v1/admin/whoami", headers={"Authorization": f"Bearer {forged}"}
    )
    assert r.status_code in (401, 403)


# ---------- ADMIN-IA-001: overview, audit, org contacts/location ----------


def _staff_headers(client, monkeypatch):
    _set_login_env(monkeypatch)
    r = client.post(
        "/api/v1/admin/login",
        json={"username": "kim", "password": "test-pass-123"},
    )
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['token']}"}


def _create_org(client, headers, **extra):
    body = {
        "name": "Sunrise Gardens",
        "contact_email": "ops@sunrise.example",
        "admin_email": "director@sunrise.example",
        "org_type": "nonprofit",
        "tier": "site",
    }
    body.update(extra)
    r = client.post("/api/v1/org/create", json=body, headers=headers)
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_overview_and_audit_staff_only(client, monkeypatch):
    headers = _staff_headers(client, monkeypatch)
    _create_org(client, headers)

    r = client.get("/api/v1/admin/overview", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["orgs_total"] >= 1
    assert "seats_total" in data and "seats_used" in data
    assert "flags_total" in data
    assert isinstance(data["licenses_expiring"], list)
    assert any(a["org_name"] == "Sunrise Gardens" for a in data["recent_audit"])

    r = client.get("/api/v1/admin/audit?q=sunrise", headers=headers)
    assert r.status_code == 200
    assert any(
        e["org_name"] == "Sunrise Gardens" and e["action"] == "org.create"
        for e in r.json()["entries"]
    )


def test_overview_rejects_non_staff(authenticated_client):
    assert authenticated_client.get("/api/v1/admin/overview").status_code == 403
    assert authenticated_client.get("/api/v1/admin/audit").status_code == 403


def test_org_create_accepts_location_and_contacts(client, monkeypatch):
    headers = _staff_headers(client, monkeypatch)
    org_id = _create_org(
        client,
        headers,
        address_line1="12 Elm St",
        city="Springfield",
        state="IL",
        postal_code="62704",
        phone="+1-217-555-0100",
        contacts=[
            {"name": "Pat Doe", "email": "pat@sunrise.example", "is_primary": True},
            {"name": "Sam Roe", "email": "sam@sunrise.example", "is_primary": True},
        ],
    )
    r = client.get(f"/api/v1/admin/orgs/{org_id}", headers=headers)
    assert r.status_code == 200
    org = r.json()["org"]
    assert org["city"] == "Springfield"
    assert org["postal_code"] == "62704"
    contacts = r.json()["contacts"]
    assert len(contacts) == 2
    # service layer collapses duplicate primaries — exactly one wins
    assert sum(1 for c in contacts if c["is_primary"]) == 1


def test_org_create_without_new_fields_still_works(client, monkeypatch):
    headers = _staff_headers(client, monkeypatch)
    org_id = _create_org(client, headers)
    r = client.get(f"/api/v1/admin/orgs/{org_id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["contacts"] == []
    assert r.json()["org"]["city"] is None
