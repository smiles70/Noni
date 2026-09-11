"""Rack 2.3: admin routes and admin_auth branch coverage backfill."""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from backend.core.config import settings
from backend.core.database import SessionLocal
from backend.models.accounts import Account
from backend.models.billing import Product, Purchase
from backend.models.governance import AccountFlag, DeletionRequest, OrgAuditLog
from backend.models.learning import Progress, Unit
from backend.models.organizations import AccessCode, Organization, OrgLicense
from backend.services import admin_auth
from backend.services.deletion import request_deletion
from backend.services.mock_parser import MOCK_NAMESPACE


def _auth_user_id(email: str) -> uuid.UUID:
    return uuid.uuid5(MOCK_NAMESPACE, email.lower())


def _create_account(
    *,
    email: str | None = None,
    staff_role: str | None = None,
    deleted_at: datetime | None = None,
    suspended_at: datetime | None = None,
) -> Account:
    """Persist an account directly and return it."""
    if email is None:
        email = f"rack23-{uuid.uuid4()}@example.com"
    db = SessionLocal()
    try:
        account = (
            db.query(Account)
            .filter(Account.auth_user_id == _auth_user_id(email))
            .first()
        )
        if account is None:
            account = Account(
                id=uuid.uuid4(),
                auth_user_id=_auth_user_id(email),
                email=email,
                display_name="Rack 23",
                staff_role=staff_role,
                deleted_at=deleted_at,
                suspended_at=suspended_at,
            )
            db.add(account)
            db.commit()
            db.refresh(account)
        return account
    finally:
        db.close()


@pytest.fixture
def admin_client(client, monkeypatch):
    """TestClient authorized via ADMIN_ACCOUNT_IDS allowlist."""
    account = _create_account(staff_role="admin")
    monkeypatch.setattr(settings, "ADMIN_ACCOUNT_IDS", str(account.id))
    client.headers.update({"Authorization": f"Bearer mock:{account.email}"})
    return client


def _set_login_env(monkeypatch, secret: str | None = "test-session-secret"):
    monkeypatch.setattr(settings, "ADMIN_CONSOLE_USERS", "kim,steven")
    monkeypatch.setattr(
        settings,
        "ADMIN_CONSOLE_PASSWORD_SHA256",
        hashlib.sha256(b"test-pass-123").hexdigest(),
    )
    monkeypatch.setattr(settings, "SESSION_SECRET", secret)


# ---------------------------------------------------------------------------
# admin_auth negative branches
# ---------------------------------------------------------------------------


def test_credentials_ok_fails_closed_with_empty_users(monkeypatch):
    """Branch: `not users` in credentials_ok guard."""
    monkeypatch.setattr(settings, "ADMIN_CONSOLE_USERS", "")
    monkeypatch.setattr(settings, "ADMIN_CONSOLE_PASSWORD_SHA256", "a" * 64)
    assert admin_auth.credentials_ok("kim", "any-pass") is False


def test_credentials_ok_fails_closed_with_bad_hash_length(monkeypatch):
    """Branch: `len(expected) != 64` in credentials_ok guard."""
    monkeypatch.setattr(settings, "ADMIN_CONSOLE_USERS", "kim")
    monkeypatch.setattr(settings, "ADMIN_CONSOLE_PASSWORD_SHA256", "tooshort")
    assert admin_auth.credentials_ok("kim", "any-pass") is False


def test_issue_staff_token_requires_secret(monkeypatch):
    """Branch: _secret() empty returns None."""
    monkeypatch.setattr(settings, "SESSION_SECRET", "")
    assert admin_auth.issue_staff_token("kim") is None


def test_verify_staff_token_requires_secret(monkeypatch):
    """Branch: _secret() empty returns None."""
    monkeypatch.setattr(settings, "SESSION_SECRET", "")
    assert admin_auth.verify_staff_token("staff.payload.sig") is None


def test_verify_staff_token_rejects_non_string(monkeypatch):
    """Branch: token not a string."""
    monkeypatch.setattr(settings, "SESSION_SECRET", "secret")
    assert admin_auth.verify_staff_token(None) is None  # type: ignore[arg-type]


def test_verify_staff_token_rejects_bad_prefix_and_shape(monkeypatch):
    """Branches: missing prefix and missing dot in body."""
    monkeypatch.setattr(settings, "SESSION_SECRET", "secret")
    assert admin_auth.verify_staff_token("not-staff") is None
    assert admin_auth.verify_staff_token("staff.nodot") is None


def test_verify_staff_token_rejects_malformed_payload_and_sig(monkeypatch):
    """Branches: payload b64 error and signature mismatch."""
    monkeypatch.setattr(settings, "SESSION_SECRET", "secret")
    # Base64 decode error -> line 94/95
    assert admin_auth.verify_staff_token("staff.bad!.sig") is None
    # Well-formed payload, wrong signature
    good = admin_auth.issue_staff_token("kim")
    assert good is not None
    forged = good[:-1] + ("A" if good[-1] != "A" else "B")
    assert admin_auth.verify_staff_token(forged) is None


def test_verify_staff_token_rejects_bad_claims(monkeypatch):
    """Branches: non-JSON claims, bad exp/username types, expired, unknown user."""
    monkeypatch.setattr(settings, "ADMIN_CONSOLE_USERS", "kim")
    monkeypatch.setattr(settings, "SESSION_SECRET", "secret")

    import base64
    import json

    def _tok(claims):
        payload = (
            base64.urlsafe_b64encode(json.dumps(claims, separators=(",", ":")).encode())
            .rstrip(b"=")
            .decode()
        )
        body = f"staff.{payload}."
        # sign with a different secret to force verify failure unless we sign properly
        body_bytes = body[6:-1].encode()  # payload bytes
        sig = (
            base64.urlsafe_b64encode(
                __import__("hmac")
                .new(b"secret", body_bytes, __import__("hashlib").sha256)
                .digest()
            )
            .rstrip(b"=")
            .decode()
        )
        return f"staff.{payload}.{sig}"

    assert admin_auth.verify_staff_token(_tok({"u": "kim"})) is None  # missing exp
    assert admin_auth.verify_staff_token(_tok({"exp": "bad", "u": "kim"})) is None
    assert admin_auth.verify_staff_token(_tok({"exp": 123, "u": 123})) is None
    assert (
        admin_auth.verify_staff_token(_tok({"exp": 1, "u": "kim"})) is None
    )  # expired
    assert (
        admin_auth.verify_staff_token(_tok({"exp": 9999999999, "u": "not-kim"})) is None
    )  # unknown user


def test_verify_staff_token_rejects_non_json_payload(monkeypatch):
    """Branch: json.loads on decoded payload raises -> lines 100/101."""
    monkeypatch.setattr(settings, "ADMIN_CONSOLE_USERS", "kim")
    monkeypatch.setattr(settings, "SESSION_SECRET", "secret")

    import base64

    payload = base64.urlsafe_b64encode(b"not-json").rstrip(b"=").decode()
    payload_bytes = payload.encode("ascii")
    sig = admin_auth._sign(payload_bytes)
    token = f"staff.{payload}.{sig}"
    assert admin_auth.verify_staff_token(token) is None


def test_staff_subject_rejects_malformed_authorization():
    """Branches: missing header, not string, not bearer, missing token."""
    assert admin_auth.staff_subject(None) is None  # type: ignore[arg-type]
    assert admin_auth.staff_subject("Basic foo") is None
    assert admin_auth.staff_subject("Bearer") is None


# ---------------------------------------------------------------------------
# Admin login edge cases
# ---------------------------------------------------------------------------


def test_admin_login_fails_when_session_secret_unset(client, monkeypatch):
    """Branch: issue_staff_token returns None => 503."""
    _set_login_env(monkeypatch, secret="")
    r = client.post(
        "/api/v1/admin/login",
        json={"username": "kim", "password": "test-pass-123"},
    )
    assert r.status_code == 503
    assert r.json()["detail"]["envelope_id"] == "admin.session_unavailable"


# ---------------------------------------------------------------------------
# whoami-check / soft staff probe
# ---------------------------------------------------------------------------


def test_whoami_check_with_valid_staff_token(client, monkeypatch):
    _set_login_env(monkeypatch)
    r = client.post(
        "/api/v1/admin/login",
        json={"username": "kim", "password": "test-pass-123"},
    )
    assert r.status_code == 200
    token = r.json()["token"]

    r = client.get(
        "/api/v1/admin/whoami-check",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["staff"] is True


def test_whoami_check_with_tampered_token_is_not_staff(client, monkeypatch):
    _set_login_env(monkeypatch)
    r = client.post(
        "/api/v1/admin/login",
        json={"username": "kim", "password": "test-pass-123"},
    )
    token = r.json()["token"]
    forged = token[:-1] + ("A" if token[-1] != "A" else "B")
    r = client.get(
        "/api/v1/admin/whoami-check",
        headers={"Authorization": f"Bearer {forged}"},
    )
    assert r.status_code == 200
    assert r.json()["staff"] is False


# ---------------------------------------------------------------------------
# Audit / flags / overview branches
# ---------------------------------------------------------------------------


def test_audit_without_query_param(admin_client):
    """Branch: admin_audit `if q` false path."""
    r = admin_client.get("/api/v1/admin/audit")
    assert r.status_code == 200
    assert "entries" in r.json()


def test_flags_open_only_filter(admin_client):
    """Branch: list_flags `if open_only` true path."""
    account = _create_account()
    db = SessionLocal()
    try:
        unresolved = AccountFlag(
            account_id=account.id, flag="scan", detail="unresolved"
        )
        resolved = AccountFlag(
            account_id=account.id,
            flag="scan",
            detail="resolved",
            resolved_at=datetime.now(timezone.utc),
            resolution_note="done",
            resolved_by=account.id,
        )
        db.add_all([unresolved, resolved])
        db.commit()
    finally:
        db.close()

    r = admin_client.get("/api/v1/admin/flags?open_only=true")
    assert r.status_code == 200
    flags = r.json()["flags"]
    assert len(flags) == 1
    assert flags[0]["flag"] == "scan"
    assert flags[0]["resolved_at"] is None


def test_flags_without_open_only(admin_client):
    """Branch: list_flags `if open_only` false path."""
    account = _create_account()
    db = SessionLocal()
    try:
        unresolved = AccountFlag(
            account_id=account.id, flag="scan", detail="unresolved"
        )
        resolved = AccountFlag(
            account_id=account.id,
            flag="scan",
            detail="resolved",
            resolved_at=datetime.now(timezone.utc),
            resolution_note="done",
            resolved_by=account.id,
        )
        db.add_all([unresolved, resolved])
        db.commit()
    finally:
        db.close()

    r = admin_client.get("/api/v1/admin/flags")
    assert r.status_code == 200
    flags = r.json()["flags"]
    # This endpoint returns all flags across tests, so only assert the
    # open_only=false branch is exercised (resolved flag is present).
    assert any(f["resolved_at"] is not None for f in flags)


def test_resolve_flag_unknown_returns_404(admin_client):
    """Branch: resolve_flag flag not found."""
    r = admin_client.post(
        f"/api/v1/admin/flags/{uuid.uuid4()}/resolve",
        json={"note": "n/a"},
    )
    assert r.status_code == 404
    assert r.json()["detail"]["envelope_id"] == "admin.flag_not_found"


# ---------------------------------------------------------------------------
# Account lifecycle branches
# ---------------------------------------------------------------------------


def test_account_suspend_reinstate_cancel_deletion_unknown_account(admin_client):
    """Branch: _account_or_404 raises 404."""
    fake_id = uuid.uuid4()
    for path in [
        f"/api/v1/admin/accounts/{fake_id}/suspend",
        f"/api/v1/admin/accounts/{fake_id}/reinstate",
        f"/api/v1/admin/accounts/{fake_id}/cancel-deletion",
    ]:
        if path.endswith("/suspend"):
            r = admin_client.post(path, json={"reason": "test"})
        else:
            r = admin_client.post(path)
        assert r.status_code == 404, f"{path}: {r.text}"


def test_account_reinstate_is_idempotent(admin_client):
    """Branch: reinstate skips already-active account."""
    account = _create_account()
    r = admin_client.post(f"/api/v1/admin/accounts/{account.id}/reinstate")
    assert r.status_code == 200
    assert r.json()["status"] == "active"
    # No audit row should be written when skipping.
    db = SessionLocal()
    try:
        count = (
            db.query(OrgAuditLog)
            .filter(
                OrgAuditLog.action == "account.reinstate",
                OrgAuditLog.detail.like(f"%account={account.id}%"),
            )
            .count()
        )
        assert count == 0
    finally:
        db.close()


def test_account_cancel_deletion_with_and_without_request(admin_client):
    """Branch: cancel_deletion req is None vs req exists."""
    no_request = _create_account()
    r = admin_client.post(f"/api/v1/admin/accounts/{no_request.id}/cancel-deletion")
    assert r.status_code == 200
    assert r.json()["status"] == "active"

    with_request = _create_account()
    db = SessionLocal()
    try:
        request_deletion(db, with_request)
        db.commit()
    finally:
        db.close()

    r = admin_client.post(f"/api/v1/admin/accounts/{with_request.id}/cancel-deletion")
    assert r.status_code == 200
    assert r.json()["status"] == "active"

    db = SessionLocal()
    try:
        req = (
            db.query(DeletionRequest)
            .filter(DeletionRequest.account_id == with_request.id)
            .first()
        )
        assert req is not None
        assert req.status == "cancelled"
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Staff role management branches
# ---------------------------------------------------------------------------


def test_staff_set_role_invalid_role(admin_client):
    """Branch: body.role not in ('admin', 'support')."""
    target = _create_account(staff_role="admin")
    r = admin_client.post(
        f"/api/v1/admin/staff/{target.id}/role",
        json={"role": "superadmin"},
    )
    assert r.status_code == 422
    assert r.json()["detail"]["envelope_id"] == "admin.invalid_role"


def test_staff_set_role_target_not_staff(admin_client):
    """Branch: target None or not staff => 404."""
    learner = _create_account()
    r = admin_client.post(
        f"/api/v1/admin/staff/{learner.id}/role",
        json={"role": "support"},
    )
    assert r.status_code == 404
    assert r.json()["detail"]["envelope_id"] == "admin.staff_not_found"


def test_staff_set_role_cannot_change_own_role(admin_client, monkeypatch):
    """Branch: target.id == staff.id => 409."""
    # Resolve the actor account id; it is allowlisted.
    actor = _create_account(email="rack23-actor@example.com", staff_role="admin")
    monkeypatch.setattr(settings, "ADMIN_ACCOUNT_IDS", str(actor.id))
    admin_client.headers.update({"Authorization": f"Bearer mock:{actor.email}"})

    r = admin_client.post(
        f"/api/v1/admin/staff/{actor.id}/role",
        json={"role": "support"},
    )
    assert r.status_code == 409
    assert r.json()["detail"]["envelope_id"] == "admin.cannot_change_own_role"


def test_staff_set_role_last_admin_guard(client, monkeypatch):
    """Branch: support downgrade with only one staff admin => 409."""
    actor = _create_account(email="rack23-lastadmin-actor@example.com")
    only_admin = _create_account(staff_role="admin")

    # Ensure only the target is counted as a staff admin.
    db = SessionLocal()
    try:
        db.query(Account).filter(
            Account.staff_role == "admin", Account.id != only_admin.id
        ).update({"staff_role": None}, synchronize_session=False)
        db.commit()
    finally:
        db.close()

    monkeypatch.setattr(settings, "ADMIN_ACCOUNT_IDS", str(actor.id))
    client.headers.update({"Authorization": f"Bearer mock:{actor.email}"})

    r = client.post(
        f"/api/v1/admin/staff/{only_admin.id}/role",
        json={"role": "support"},
    )
    assert r.status_code == 409
    assert r.json()["detail"]["envelope_id"] == "admin.last_admin"


def test_staff_set_role_success_and_idempotent(admin_client, monkeypatch):
    """Branches: successful role change and idempotent no-op."""
    actor = _create_account(email="rack23-role-actor@example.com")
    monkeypatch.setattr(settings, "ADMIN_ACCOUNT_IDS", str(actor.id))
    admin_client.headers.update({"Authorization": f"Bearer mock:{actor.email}"})

    # Two staff admins so downgrading one is safe.
    _create_account(staff_role="admin")
    target = _create_account(staff_role="admin")

    r = admin_client.post(
        f"/api/v1/admin/staff/{target.id}/role",
        json={"role": "support"},
    )
    assert r.status_code == 200
    assert r.json()["role"] == "support"

    r = admin_client.post(
        f"/api/v1/admin/staff/{target.id}/role",
        json={"role": "support"},
    )
    assert r.status_code == 200
    assert r.json()["role"] == "support"


# ---------------------------------------------------------------------------
# org-activity report branches
# ---------------------------------------------------------------------------


def _seed_org_with_learner() -> tuple[uuid.UUID, Account]:
    """Create org, license, claimed code, learner, and unit."""
    account = _create_account(email=f"rack23-learner-{uuid.uuid4()}@example.com")
    product_code = f"rack23-prod-{uuid.uuid4()}"
    db = SessionLocal()
    try:
        product = Product(
            code=product_code,
            display_name="Rack product",
            price_cents=100,
            currency="usd",
            active=True,
            content_version=1,
        )
        purchase = Purchase(
            product_code=product_code,
            amount_cents=100,
            currency="usd",
            status="paid",
            buyer_account_id=account.id,
        )
        org = Organization(
            name="Rack Org",
            contact_email=account.email,
            admin_email=account.email,
            status="active",
            org_type="nonprofit",
            tier="site",
        )
        license_ = OrgLicense(
            organization=org,
            product_code=product_code,
            purchase=purchase,
            total_seats=5,
            used_seats=1,
        )
        code = AccessCode(
            license=license_,
            code_hash=f"rack23-code-{uuid.uuid4()}",
            claimed_by_account_id=account.id,
            claimed_at=datetime.now(timezone.utc),
        )
        db.add_all([product, purchase, org, license_, code])
        db.flush()
        org_id = org.id
        db.commit()
    finally:
        db.close()
    return org_id, account


def test_org_activity_report_with_no_learners(admin_client):
    """Branch: prog_q is None (no claimed codes / learners)."""
    org_id, _ = _seed_org_with_learner()
    # Wipe the claimed code so the org has a license but no learners.
    db = SessionLocal()
    try:
        code = (
            db.query(AccessCode)
            .filter(
                AccessCode.license_id.in_(
                    db.query(OrgLicense.id).filter(OrgLicense.organization_id == org_id)
                )
            )
            .first()
        )
        if code:
            code.claimed_by_account_id = None
            code.claimed_at = None
            db.commit()
    finally:
        db.close()

    r = admin_client.get(f"/api/v1/admin/reports/org-activity?org_id={org_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["window_days"] == 30
    assert len(data["orgs"]) == 1
    assert data["orgs"][0]["learners_enrolled"] == 0
    assert data["orgs"][0]["last_activity_utc"] is None


def test_org_activity_report_with_progress_branches(admin_client):
    """Branches: completed in window, active learner, last_activity update."""
    org_id, learner = _seed_org_with_learner()
    now = datetime.now(timezone.utc)

    unit_started = f"rack23-unit-started-{uuid.uuid4()}"
    unit_completed = f"rack23-unit-completed-{uuid.uuid4()}"
    unit_old = f"rack23-unit-old-{uuid.uuid4()}"

    db = SessionLocal()
    try:
        db.add_all(
            [
                Unit(
                    id=unit_started,
                    module_code="rack23",
                    unit_index=0,
                    title="Started only",
                ),
                Unit(
                    id=unit_completed,
                    module_code="rack23",
                    unit_index=1,
                    title="Completed",
                ),
                Unit(
                    id=unit_old,
                    module_code="rack23",
                    unit_index=2,
                    title="Old",
                ),
            ]
        )
        db.flush()

        # Completed within window: covers completed>=window_start and
        # active-learner branch, plus last_activity update from completed.
        db.add(
            Progress(
                account_id=learner.id,
                unit_id=unit_completed,
                status="completed",
                content_version=1,
                first_started_at=now - timedelta(days=2),
                completed_at=now - timedelta(days=1),
            )
        )
        # Started only: covers completed is None (one ts is None) and
        # last_activity update from started.
        db.add(
            Progress(
                account_id=learner.id,
                unit_id=unit_started,
                status="started",
                content_version=1,
                first_started_at=now - timedelta(days=3),
                completed_at=None,
            )
        )
        # Before window: both timestamps outside the window, covering the
        # active-learner false branch.
        db.add(
            Progress(
                account_id=learner.id,
                unit_id=unit_old,
                status="completed",
                content_version=1,
                first_started_at=now - timedelta(days=60),
                completed_at=now - timedelta(days=50),
            )
        )
        db.commit()
    finally:
        db.close()

    r = admin_client.get(f"/api/v1/admin/reports/org-activity?org_id={org_id}")
    assert r.status_code == 200
    data = r.json()
    assert len(data["orgs"]) == 1
    org = data["orgs"][0]
    assert org["learners_enrolled"] == 1
    assert org["active_learners_in_window"] == 1
    assert org["units_completed_in_window"] == 1
    assert org["last_activity_utc"] is not None
