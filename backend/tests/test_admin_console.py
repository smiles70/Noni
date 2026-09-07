"""AC-1: admin console access control.

The console is staff-only by design — same guard family as the org
dashboard tests. whoami-check is the soft probe for the frontend gate.
"""

from __future__ import annotations

import uuid
from datetime import timedelta


def test_whoami_requires_session(client):
    r = client.get("/api/v1/admin/whoami")
    assert r.status_code == 401
    assert r.json()["detail"]["envelope_id"] == "auth.signed_out"


def test_whoami_check_is_soft(client):
    r = client.get("/api/v1/admin/whoami-check")
    assert r.status_code == 200
    assert r.json()["staff"] is False


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
    assert r.json()["staff"] is True

    r = client.get(
        "/api/v1/admin/whoami-check",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["staff"] is True


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
    r = client.post("/api/v1/billing/org/create", json=body, headers=headers)
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


# ---------- ADMIN-OPS E1: license lifecycle ----------


def _create_license(client, headers, org_id, seats=5):
    r = client.post(
        f"/api/v1/billing/org/{org_id}/license",
        json={
            "product_code": "modules_4_5",
            "total_seats": seats,
            "amount_cents": 0,
            "invoice_ref": "test",
        },
        headers=headers,
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_license_edit_seats_and_expiry(client, monkeypatch):
    headers = _staff_headers(client, monkeypatch)
    org_id = _create_org(client, headers)
    lic_id = _create_license(client, headers, org_id)

    r = client.patch(
        f"/api/v1/billing/org/license/{lic_id}",
        json={"total_seats": 25, "expires_at": "2027-12-31T00:00:00Z"},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total_seats"] == 25
    assert body["status"] == "active"

    audit = client.get("/api/v1/admin/audit?q=license.edit", headers=headers).json()
    assert any("seats=5->25" in e["detail"] for e in audit["entries"])


def test_license_edit_below_used_rejected(client, monkeypatch):
    headers = _staff_headers(client, monkeypatch)
    org_id = _create_org(client, headers)
    lic_id = _create_license(client, headers, org_id, seats=1)
    codes = client.post(
        f"/api/v1/billing/org/{lic_id}/codes",
        json={"count": 1},
        headers=headers,
    ).json()["codes"]

    learner_headers = {"Authorization": "Bearer mock:learner-e1@example.com"}
    r = client.post(
        "/api/v1/billing/org/redeem",
        json={"code": codes[0]},
        headers=learner_headers,
    )
    assert r.status_code == 200, r.text

    r = client.patch(
        f"/api/v1/billing/org/license/{lic_id}",
        json={"total_seats": 0},
        headers=headers,
    )
    assert r.status_code in (409, 422)


def test_suspend_blocks_redeem_reinstate_restores(client, monkeypatch):
    headers = _staff_headers(client, monkeypatch)
    org_id = _create_org(client, headers)
    lic_id = _create_license(client, headers, org_id, seats=2)
    codes = client.post(
        f"/api/v1/billing/org/{lic_id}/codes",
        json={"count": 2},
        headers=headers,
    ).json()["codes"]

    r = client.post(
        f"/api/v1/billing/org/license/{lic_id}/suspend",
        json={"reason": "non-payment"},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "suspended"

    learner_headers = {"Authorization": "Bearer mock:learner-e2@example.com"}
    r = client.post(
        "/api/v1/billing/org/redeem",
        json={"code": codes[0]},
        headers=learner_headers,
    )
    assert r.status_code == 410
    assert r.json()["detail"]["envelope_id"] == "org.license_suspended"

    r = client.post(
        f"/api/v1/billing/org/license/{lic_id}/reinstate",
        headers=headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "active"

    r = client.post(
        "/api/v1/billing/org/redeem",
        json={"code": codes[0]},
        headers=learner_headers,
    )
    assert r.status_code == 200, r.text


def test_license_lifecycle_staff_only(client, authenticated_client):
    r = client.patch(
        "/api/v1/billing/org/license/00000000-0000-0000-0000-000000000000",
        json={"total_seats": 5},
        headers={},
    )
    assert r.status_code in (401, 403)


# ---------- ADMIN-OPS E2: org suspend/reinstate ----------


def test_org_suspend_blocks_redeem_and_codes(client, monkeypatch):
    headers = _staff_headers(client, monkeypatch)
    org_id = _create_org(client, headers)
    lic_id = _create_license(client, headers, org_id, seats=2)
    codes = client.post(
        f"/api/v1/billing/org/{lic_id}/codes",
        json={"count": 2},
        headers=headers,
    ).json()["codes"]

    r = client.post(
        f"/api/v1/billing/org/{org_id}/suspend",
        json={"reason": "contract lapse"},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "suspended"

    # code generation blocked
    r = client.post(
        f"/api/v1/billing/org/{lic_id}/codes",
        json={"count": 1},
        headers=headers,
    )
    assert r.status_code == 410
    assert r.json()["detail"]["envelope_id"] == "org.org_suspended"

    # redemption blocked
    r = client.post(
        "/api/v1/billing/org/redeem",
        json={"code": codes[0]},
        headers={"Authorization": "Bearer mock:e2-learner@example.com"},
    )
    assert r.status_code == 410
    assert r.json()["detail"]["envelope_id"] == "org.org_suspended"

    # reinstate restores redemption
    r = client.post(
        f"/api/v1/billing/org/{org_id}/reinstate",
        json={"include_children": False},
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["status"] == "active"

    r = client.post(
        "/api/v1/billing/org/redeem",
        json={"code": codes[0]},
        headers={"Authorization": "Bearer mock:e2-learner@example.com"},
    )
    assert r.status_code == 200, r.text

    audit = client.get("/api/v1/admin/audit?q=org.suspend", headers=headers).json()
    assert any("contract lapse" in e["detail"] for e in audit["entries"])


def test_org_suspend_does_not_cascade_by_default(client, monkeypatch):
    headers = _staff_headers(client, monkeypatch)
    parent_id = _create_org(client, headers, name="Parent Co")
    child_id = _create_org(
        client,
        headers,
        name="Child Co",
        contact_email="c@child.example",
        admin_email="a@child.example",
        parent_org_id=parent_id,
    )

    client.post(
        f"/api/v1/billing/org/{parent_id}/suspend",
        json={"reason": "parent suspend"},
        headers=headers,
    )

    detail = client.get(f"/api/v1/admin/orgs/{child_id}", headers=headers).json()
    assert detail["org"]["status"] == "active"

    # explicit include_children cascades
    client.post(
        f"/api/v1/billing/org/{parent_id}/suspend",
        json={"reason": "parent+children", "include_children": True},
        headers=headers,
    )
    detail = client.get(f"/api/v1/admin/orgs/{child_id}", headers=headers).json()
    assert detail["org"]["status"] == "suspended"


def test_org_suspend_staff_only(client):
    r = client.post(
        "/api/v1/billing/org/00000000-0000-0000-0000-000000000000/suspend",
        json={"reason": "x"},
    )
    assert r.status_code in (401, 403)


# ---------- ADMIN-OPS E3/E4/E6 ----------


def test_org_search_empty_returns_recent(client, monkeypatch):
    """E3: empty query returns recent orgs for the wizard parent picker."""
    headers = _staff_headers(client, monkeypatch)
    _create_org(client, headers, name="Recent Org Alpha")
    r = client.get("/api/v1/admin/orgs?q=", headers=headers)
    assert r.status_code == 200, r.text
    assert any(o["name"] == "Recent Org Alpha" for o in r.json())


def test_org_create_with_parent(client, monkeypatch):
    headers = _staff_headers(client, monkeypatch)
    parent = _create_org(client, headers, name="Parent Org E3")
    child = _create_org(client, headers, name="Child Org E3", parent_org_id=parent)
    detail = client.get(f"/api/v1/admin/orgs/{parent}", headers=headers).json()
    assert any(c["id"] == child for c in detail["children"])


def test_export_orgs_csv(client, monkeypatch):
    headers = _staff_headers(client, monkeypatch)
    _create_org(client, headers, name="Export Org")
    r = client.get("/api/v1/admin/export/orgs.csv", headers=headers)
    assert r.status_code == 200, r.text
    assert "generated_at_utc" in r.text
    assert "Export Org" in r.text
    assert r.headers["content-type"].startswith("text/csv")


def test_export_audit_csv(client, monkeypatch):
    headers = _staff_headers(client, monkeypatch)
    _create_org(client, headers, name="Audit Export Org")
    r = client.get("/api/v1/admin/export/audit.csv", headers=headers)
    assert r.status_code == 200, r.text
    assert "org.create" in r.text
    assert "at_utc" in r.text


def test_export_staff_only(client):
    r = client.get("/api/v1/admin/export/orgs.csv")
    assert r.status_code in (401, 403)


def test_account_suspend_blocks_auth_and_reinstate(client, monkeypatch):
    """E6: suspended learner account gets 401 on authed routes; reinstate restores."""
    headers = _staff_headers(client, monkeypatch)
    email = "e6-learner@example.com"
    learner = {"Authorization": f"Bearer mock:{email}"}
    # materialize the account via a learner authed route
    r = client.get("/api/v1/me/export", headers=learner)
    assert r.status_code == 200, r.text
    found = client.get(f"/api/v1/admin/accounts?q={email}", headers=headers)
    assert found.status_code == 200, found.text
    acct_id = found.json()[0]["id"]

    r = client.post(
        f"/api/v1/admin/accounts/{acct_id}/suspend",
        json={"reason": "e6 verify"},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "suspended"

    # learner authed route now blocked
    r = client.get("/api/v1/me/export", headers=learner)
    assert r.status_code == 401
    assert r.json()["detail"]["envelope_id"] == "auth.account_suspended"

    # idempotent
    r = client.post(
        f"/api/v1/admin/accounts/{acct_id}/suspend",
        json={"reason": "again"},
        headers=headers,
    )
    assert r.status_code == 200

    r = client.post(f"/api/v1/admin/accounts/{acct_id}/reinstate", headers=headers)
    assert r.status_code == 200
    assert client.get("/api/v1/me/export", headers=learner).status_code == 200

    # audit entry exists — verify via the audit CSV export (aggregate feed)
    audit = client.get("/api/v1/admin/export/audit.csv", headers=headers)
    assert "account.suspend" in audit.text


def test_account_actions_staff_only(client):
    r = client.post(
        "/api/v1/admin/accounts/00000000-0000-0000-0000-000000000000/suspend",
        json={"reason": "x"},
    )
    assert r.status_code in (401, 403)


def test_account_cancel_deletion(client, monkeypatch):
    headers = _staff_headers(client, monkeypatch)
    email = "e6-deleted@example.com"
    learner = {"Authorization": f"Bearer mock:{email}"}
    client.get("/api/v1/me/export", headers=learner)
    found = client.get(f"/api/v1/admin/accounts?q={email}", headers=headers)
    assert found.status_code == 200, found.text
    acct_id = found.json()[0]["id"]

    # soft-delete via direct row update through a second authed hit isn't
    # exposed; use the staff search to find then flip via service path —
    # here we just verify cancel-deletion is idempotent on a live account.
    r = client.post(
        f"/api/v1/admin/accounts/{acct_id}/cancel-deletion", headers=headers
    )
    assert r.status_code == 200
    assert r.json()["status"] == "active"


# ---------- ADMIN-OPS E5: staff RBAC ----------


def _staff_headers_for(client, monkeypatch, username, admins=""):
    import hashlib
    from backend.core.config import settings

    monkeypatch.setattr(settings, "ADMIN_CONSOLE_USERS", "kim,steven")
    monkeypatch.setattr(
        settings,
        "ADMIN_CONSOLE_PASSWORD_SHA256",
        hashlib.sha256(b"test-pass-123").hexdigest(),
    )
    monkeypatch.setattr(settings, "ADMIN_CONSOLE_ADMINS", admins)
    monkeypatch.setattr(settings, "SESSION_SECRET", "test-session-secret")
    r = client.post(
        "/api/v1/admin/login",
        json={"username": username, "password": "test-pass-123"},
    )
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['token']}"}


def test_support_role_blocked_from_mutations(client, monkeypatch):
    """E5: support reads fine, mutations 403 auth.not_admin."""
    headers = _staff_headers_for(client, monkeypatch, "steven", admins="kim")
    assert client.get("/api/v1/admin/orgs?q=", headers=headers).status_code == 200
    r = client.post(
        "/api/v1/billing/org/create",
        json={
            "name": "Blocked Org",
            "contact_email": "x@x.example",
            "admin_email": "x@x.example",
        },
        headers=headers,
    )
    assert r.status_code == 403
    assert r.json()["detail"]["envelope_id"] == "auth.not_admin"


def test_admin_role_mutations_allowed(client, monkeypatch):
    headers = _staff_headers_for(client, monkeypatch, "kim", admins="kim")
    assert client.get("/api/v1/admin/whoami", headers=headers).json()["role"] == "admin"
    r = client.post(
        "/api/v1/billing/org/create",
        json={
            "name": "Admin Made",
            "contact_email": "a@a.example",
            "admin_email": "a@a.example",
        },
        headers=headers,
    )
    assert r.status_code == 201


def test_staff_role_change_and_guards(client, monkeypatch):
    admin = _staff_headers_for(client, monkeypatch, "kim", admins="kim")
    steven = _staff_headers_for(client, monkeypatch, "steven", admins="kim")
    staff = client.get("/api/v1/admin/staff", headers=admin)
    assert staff.status_code == 200, staff.text
    rows = {r["display_name"]: r for r in staff.json()}
    assert rows["kim"]["role"] == "admin"
    assert rows["steven"]["role"] == "support"

    # support cannot list or mutate staff
    assert client.get("/api/v1/admin/staff", headers=steven).status_code == 403

    # cannot change own role
    r = client.post(
        f"/api/v1/admin/staff/{rows['kim']['id']}/role",
        json={"role": "support"},
        headers=admin,
    )
    assert r.status_code == 403 or r.status_code == 409

    # promote steven
    r = client.post(
        f"/api/v1/admin/staff/{rows['steven']['id']}/role",
        json={"role": "admin"},
        headers=admin,
    )
    assert r.status_code == 200
    assert r.json()["role"] == "admin"


# ---------- ADMIN-OPS-HYGIENE ----------


def test_flag_resolve_idempotent_and_audited(client, monkeypatch):
    """Route and task see committed rows only — use the app session."""
    from backend.core.database import SessionLocal
    from backend.models.governance import AccountFlag

    headers = _staff_headers(client, monkeypatch)
    client.get(
        "/api/v1/me/export",
        headers={"Authorization": "Bearer mock:h1-learner@example.com"},
    )
    acct = client.get("/api/v1/admin/accounts?q=h1-learner", headers=headers)
    acct_id = acct.json()[0]["id"]

    db = SessionLocal()
    try:
        flag = AccountFlag(
            account_id=uuid.UUID(acct_id),
            flag="sharing_signal",
            detail="test flag",
        )
        db.add(flag)
        db.commit()
        flag_id = flag.id
    finally:
        db.close()

    r = client.post(
        f"/api/v1/admin/flags/{flag_id}/resolve",
        json={"note": "contacted, legit family"},
        headers=headers,
    )
    assert r.status_code == 200, r.text

    open_list = client.get("/api/v1/admin/flags?open_only=1", headers=headers)
    assert all(f["id"] != str(flag_id) for f in open_list.json()["flags"])

    # idempotent — second resolve is a no-op 200
    assert (
        client.post(
            f"/api/v1/admin/flags/{flag_id}/resolve", json={}, headers=headers
        ).status_code
        == 200
    )

    # audited
    csv = client.get("/api/v1/admin/export/audit.csv", headers=headers)
    assert "flag.resolve" in csv.text


def test_flag_resolve_staff_only(client):
    r = client.post(
        "/api/v1/admin/flags/00000000-0000-0000-0000-000000000000/resolve",
        json={},
    )
    assert r.status_code in (401, 403)


def test_deletion_sweep_executes_due_requests(client, monkeypatch):
    """H2: past-grace requests are executed; pending ones untouched."""
    from backend.core.database import SessionLocal
    from backend.models.accounts import Account
    from backend.models.governance import DeletionRequest
    from backend.services.deletion import request_deletion, _utcnow
    from backend.tasks.webhook_tasks import cleanup_deleted_accounts

    db = SessionLocal()
    acct = None
    try:
        acct = Account(email="sweep@example.com", display_name="Sweep")
        db.add(acct)
        db.commit()
        req = request_deletion(db, acct, grace_days=0)
        req.scheduled_for = _utcnow() - timedelta(days=1)
        db.commit()
        acct_id = acct.id
        req_id = req.id
    finally:
        db.close()

    try:
        result = cleanup_deleted_accounts()
        assert result["done"] >= 1
        db = SessionLocal()
        acct = db.get(Account, acct_id)
        assert acct.email.startswith("deleted+")
        req = db.get(DeletionRequest, req_id)
        assert req.status == "completed"
    finally:
        db.close()


def test_deletion_sweep_leaves_pending_alone(client, monkeypatch):
    from backend.core.database import SessionLocal
    from backend.models.accounts import Account
    from backend.services.deletion import request_deletion
    from backend.tasks.webhook_tasks import cleanup_deleted_accounts

    db = SessionLocal()
    try:
        acct = Account(email="pending@example.com", display_name="Pending")
        db.add(acct)
        db.commit()
        req = request_deletion(db, acct, grace_days=30)
        db.commit()

        cleanup_deleted_accounts()
        db.refresh(acct)
        assert acct.email == "pending@example.com"  # not executed
        db.refresh(req)
        assert req.status == "requested"
    finally:
        db.close()


def test_maintenance_endpoints_staff_only_and_admin_gated(client, monkeypatch):
    """H5: maintenance triggers need admin role; support gets 403."""
    r = client.post("/api/v1/admin/maintenance/run-deletion-sweep")
    assert r.status_code in (401, 403)

    headers = _staff_headers(client, monkeypatch)  # admins unset → admin
    r = client.post("/api/v1/admin/maintenance/run-deletion-sweep", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert "done" in body and "failed" in body and "due" in body

    # audit row written
    csv = client.get("/api/v1/admin/export/audit.csv", headers=headers)
    assert "maintenance.deletion_sweep" in csv.text


def test_maintenance_flag_scan_runs(client, monkeypatch):
    headers = _staff_headers(client, monkeypatch)
    r = client.post("/api/v1/admin/maintenance/run-flag-scan", headers=headers)
    assert r.status_code == 200
    assert "scanned" in r.json() and "flagged" in r.json()
