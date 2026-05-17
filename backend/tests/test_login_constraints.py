"""Login domain — backend acceptance test skeleton.

Source of truth:
    docs/audits/login-system-constraints-2026-05-17.md  (§14 acceptance suite)
    docs/audits/login-constraint-refinement-2026-05-17.md  (test ↔ constraint map)
    Tag: login-constraints-v1

Scope split:
    Backend tests cover the verifier, account materialization, deletion
    semantics, race conditions, and observability constraints. Frontend
    tests (auth-state ownership, view transitions, chrome/body
    consistency) live in
    `frontend/src/__tests__/login_contract.test.ts`.

Each test below is a stub. Bodies are intentionally empty so redesign
can fill them in TDD-style. Every stub:
  - states the user/system action,
  - states the expected behavior,
  - lists forbidden outcomes,
  - cites the constraints/invariants/failure-modes it validates.

Tests are marked `xfail(strict=True)` so the suite is committable today
without going green prematurely; redesign work flips them to passing
one at a time.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event

from backend.app.main import app
from backend.core.config import settings
from backend.core.database import SessionLocal
from backend.models.accounts import Account


# Stage 2+ promoted tests require Postgres (UUID, CITEXT, partial index)
# and the M1 schema (accounts.email NULL, no uq_accounts_email). Mirror
# the gate used by other DB-dependent suites.
_requires_postgres = pytest.mark.skipif(
    "sqlite" in (os.environ.get("DATABASE_URL") or settings.DATABASE_URL),
    reason="Stage 2 acceptance tests require Postgres with M1 applied.",
)


# ---------------------------------------------------------------------------
# A. Critical path
# ---------------------------------------------------------------------------


@pytest.mark.xfail(strict=True, reason="redesign-pending: T-A1")
def test_T_A1_returning_user_reaches_success_state() -> None:
    """T-A1 — Returning user with a valid provider session opens the app.

    Action:
        Boot the app with a previously-materialized account whose
        provider session is valid; observe end state.

    Expected:
        Reaches SUCCESS_STATE; whoami returns 200 with stable account
        identifier; visible curriculum entry corresponds to the
        persisted progress for that account.

    Forbidden:
        Any frame in which the user is shown SIGNIN; any whoami response
        that is not 200; any extra whoami call beyond the one budgeted
        per boot.

    Validates: B1, B3, B11, B12, T1, T3, T7, R3 ; I-A, I-G, I-J
    Prevents:  F1 (existing user), F8, FC1 (existing user)
    """
    raise NotImplementedError


@pytest.mark.xfail(strict=True, reason="redesign-pending: T-A2")
def test_T_A2_new_user_completes_provider_signup() -> None:
    """T-A2 — Brand-new user completes provider sign-up.

    Action:
        Drive the provider's sign-up completion event for a subject
        that has no account row yet.

    Expected:
        Reaches SUCCESS_STATE; lands on curriculum entry with
        progress=clean; whoami returns 200 once.

    Forbidden:
        SIGNIN re-rendered after completion; whoami called more than
        once before render; any 401 surfaced; any DB write performed
        on the read path itself (materialization must be on a write
        event).

    Validates: B4, B5, B12, T6 ; I-A, I-B
    Prevents:  FC1 (new user), F2 (when secret present)
    """
    raise NotImplementedError


@pytest.mark.xfail(strict=True, reason="redesign-pending: T-A3")
def test_T_A3_critical_path_with_optional_secret_unavailable() -> None:
    """T-A3 — Existing user signs in with optional secret unavailable.

    Action:
        Account already materialized. Unset the optional provider
        Backend-API secret. Drive a sign-in.

    Expected:
        Sign-in succeeds; reaches SUCCESS_STATE.

    Forbidden:
        401 on the critical path; redirect to SIGNIN; any "stuck"
        loading state; any dependency on the optional secret.

    Validates: B11, B12, C1, C5, R5 ; I-H
    Prevents:  F2, F4 (existing-user branch)
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# B. Auth correctness
# ---------------------------------------------------------------------------


@pytest.mark.xfail(strict=True, reason="redesign-pending: T-B1")
def test_T_B1_provider_signed_in_backend_transient_5xx() -> None:
    """T-B1 — Provider signed-in; backend returns transient 5xx.

    Action:
        Inject a 5xx on a protected route while the provider still
        reports signed-in.

    Expected:
        Auth state does NOT flip to signed-out; user stays on current
        view; transient-error surface is shown with a discriminated
        reason code.

    Forbidden:
        Any redirect to SIGNIN; any view eviction; any auto-retry
        burst; any 5xx body that is indistinguishable from a 401.

    Validates: B5, R1, R3 ; I-A
    Prevents:  F1, F3, FC1, FC2
    """
    raise NotImplementedError


@pytest.mark.xfail(strict=True, reason="redesign-pending: T-B2")
def test_T_B2_provider_signed_out_in_another_tab() -> None:
    """T-B2 — Provider signed-out in another tab.

    Action:
        Trigger a provider sign-out event on a tab that is currently
        showing a signed-in surface.

    Expected:
        Tab transitions to LANDING_OUT exactly once; chrome and body
        agree on signedIn=false within a single render commit.

    Forbidden:
        Any rendered frame in which chrome and body disagree about
        signedIn; any oscillation back to signed-in.

    Validates: B1, B6 ; I-C, I-G
    Prevents:  F8, FC5
    """
    raise NotImplementedError


@_requires_postgres
def test_T_B3_token_rejected_by_signature_or_exp() -> None:
    """T-B3 — Token rejected by signature/exp.

    Action:
        Present a token that fails verification (under mock provider:
        a malformed token; the Clerk equivalent is bad signature OR
        expired); make a request to the read-only session resolver.

    Expected:
        Response carries a discriminated reason code (one of
        `auth.malformed`, `auth.signature_invalid`, `auth.expired`,
        `auth.no_credential`); envelope is `{"detail": {"error":
        {"code", "message"}}}`; status 401.

    Forbidden:
        Indistinguishable 401 (no code field); 5xx; 2xx; raw string
        envelope.

    Validates: B5, R1, R4 ; I-A, I-I
    """
    client = TestClient(app)

    # 1. No credential at all → auth.no_credential.
    r = client.get("/auth/session")
    assert r.status_code == 401, r.text
    body = r.json()
    assert "detail" in body and "error" in body["detail"], body
    assert body["detail"]["error"]["code"] == "auth.no_credential"
    assert isinstance(body["detail"]["error"]["message"], str)

    # 2. Bearer with a non-mock token → auth.malformed (B5: not a
    # generic 401; the reason is discriminated).
    r = client.get(
        "/auth/session",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )
    assert r.status_code == 401, r.text
    body = r.json()
    code = body["detail"]["error"]["code"]
    # The set is closed (auth_verifier.CODES) so any valid discriminated
    # code passes. We assert a non-empty value in the namespace.
    assert isinstance(code, str) and code.startswith("auth."), code
    assert code != "auth.no_credential", "must discriminate from missing header"

    # 3. "Bearer " with no token body → auth.no_credential (the parser
    # rejects empty tokens before the verifier sees them).
    r = client.get("/auth/session", headers={"Authorization": "Bearer "})
    assert r.status_code == 401, r.text
    assert r.json()["detail"]["error"]["code"] == "auth.no_credential"

    # 4. Wrong scheme → also no_credential (parser rejects).
    r = client.get("/auth/session", headers={"Authorization": "Basic mock:x@y.z"})
    assert r.status_code == 401, r.text
    assert r.json()["detail"]["error"]["code"] == "auth.no_credential"


# ---------------------------------------------------------------------------
# C. State transitions
# ---------------------------------------------------------------------------


@pytest.mark.xfail(strict=True, reason="redesign-pending: T-C1")
def test_T_C1_every_reachable_view_has_exit() -> None:
    """T-C1 — Probe every reachable view for an exit transition.

    Action:
        Statically (or by exhaustive probing) enumerate every view
        value the application can hold.

    Expected:
        Each reachable view has at least one user-visible exit (Back,
        Cancel, or completion).

    Forbidden:
        Any view whose only exit is page reload.

    Validates: B9, C4
    Prevents:  F9, audit §7 dead-end class
    """
    raise NotImplementedError


@pytest.mark.xfail(strict=True, reason="redesign-pending: T-C2")
def test_T_C2_oauth_finishing_unreachable_or_removed() -> None:
    """T-C2 — Attempt to enter OAUTH_FINISHING.

    Expected:
        State is unreachable (or removed entirely from the view enum).

    Forbidden:
        State reachable but has no exit transition.

    Validates: B9
    Prevents:  F9
    """
    raise NotImplementedError


@pytest.mark.xfail(strict=True, reason="redesign-pending: T-C3")
def test_T_C3_force_FC1_chain_is_bounded() -> None:
    """T-C3 — Force FC1 (provider signed-in + whoami 401).

    Action:
        Construct a state where the provider reports signed-in but
        whoami returns 401 for a deterministic, surfaced reason.

    Expected:
        A bounded number of transitions, then the system settles on a
        stable, surfaced-error state.

    Forbidden:
        SIGNIN ↔ GATED_LOCKED oscillation across more than one cycle;
        any auto-issued repeat of the same failing protected request.

    Validates: I-I, R2, R7
    Prevents:  FC1 oscillation
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# D. Temporal
# ---------------------------------------------------------------------------


@pytest.mark.xfail(strict=True, reason="redesign-pending: T-D2")
def test_T_D2_FE_BE_provider_mismatch_aborts_boot() -> None:
    """T-D2 — Boot with mismatched FE/BE provider.

    Action:
        Configure backend `AUTH_PROVIDER` to a value different from the
        FE-baked `VITE_AUTH_PROVIDER` token (passed via a startup
        probe / asserted bundle field).

    Expected:
        Deployment startup fails loudly (probe rejects the boot); no
        user-visible 401 cascade.

    Forbidden:
        Silent 401 storm; user-visible authenticated traffic before
        the parity check has run.

    Validates: B3, T4
    Prevents:  F6 mismatch class
    """
    raise NotImplementedError


# Note: T-D1 is purely frontend-timing and lives in the FE skeleton.


# ---------------------------------------------------------------------------
# E. Failure & recovery
# ---------------------------------------------------------------------------


@pytest.mark.xfail(strict=True, reason="redesign-pending: T-E1")
def test_T_E1_single_jwks_outage_does_not_evict_user() -> None:
    """T-E1 — Single JWKS network outage during a session.

    Action:
        For an existing-user session, simulate a transient JWKS
        unreachable window.

    Expected:
        Existing user's view does not regress; explicit transient
        surface; bounded behavior (no infinite retry).

    Forbidden:
        Forced sign-in; forced sign-out; infinite retry; any 401 with
        no discriminated reason.

    Validates: B5, C2, R3, R7 ; I-A, I-I
    Prevents:  F1, F3
    """
    raise NotImplementedError


@pytest.mark.xfail(strict=True, reason="redesign-pending: T-E2")
def test_T_E2_provider_backend_api_unreachable_existing_users_unaffected() -> None:
    """T-E2 — Provider Backend API unreachable.

    Action:
        With the provider's Backend API mocked unreachable, exercise
        whoami / protected calls for already-materialized users.

    Expected:
        All already-materialized users continue to function.

    Forbidden:
        Any signed-in user perceives a denial of service; any failure
        of an optional dependency cascades to the success path.

    Validates: C2, C3, C5, R5 ; I-H
    Prevents:  F4
    """
    raise NotImplementedError


@pytest.mark.xfail(strict=True, reason="redesign-pending: T-E3")
def test_T_E3_db_unavailable_isolates_to_db_routes() -> None:
    """T-E3 — DB unavailable for a brief window.

    Action:
        Knock the DB unavailable for ~1s; exercise both DB-touching
        and non-DB routes (e.g., public landing envelopes).

    Expected:
        Failures discriminated; no cross-route propagation; landing
        page envelopes still load.

    Forbidden:
        Signed-in users evicted to SIGNIN solely due to DB downtime;
        any DB-write attempted from a route documented as read-only.

    Validates: R6 ; boundary §11.3
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# G. Account lifecycle
# ---------------------------------------------------------------------------


@pytest.mark.xfail(strict=True, reason="redesign-pending: T-G1")
def test_T_G1_deleted_account_cannot_resurrect_via_subsequent_token() -> None:
    """T-G1 — Delete account, then attempt to sign in again with same
    provider subject.

    Action:
        Mark an account deleted via the deletion endpoint. Then present
        a fresh, otherwise-valid token from the same provider subject.

    Expected:
        Cannot resurrect; an explicit "create new account" surface is
        required for re-creation.

    Forbidden:
        Silent re-creation of an account row; access to the previously
        deleted user's progress; any lookup path that returns the
        soft-deleted row.

    Validates: B7 ; I-E
    Prevents:  FC4
    """
    raise NotImplementedError


@_requires_postgres
def test_T_G2_two_subjects_sharing_email_do_not_silently_relink() -> None:
    """T-G2 — Two distinct provider subjects share an email.

    Action:
        Seed account A directly (subject S1, email E). Then POST
        /auth/session/init with a mock token for a DIFFERENT subject
        (S2, same email E).

    Expected:
        A second row materializes for S2 (M1 dropped the email UNIQUE
        constraint so this is structurally permitted); account A's
        `auth_user_id` is unchanged; (subject → row) mapping remains
        monotonic.

    Forbidden:
        Silent ownership transfer (account A's auth_user_id rewritten
        to S2); account A left orphaned (deleted_at set); any update
        to account A whatsoever.

    Validates: B8 ; I-D
    Prevents:  FC3 (Race B)
    """
    shared_email = f"t-g2-shared-{uuid.uuid4().hex[:8]}@example.test"
    s1_subject_uuid = uuid.uuid4()  # NOT derived from email (distinct from mock)
    s2_email_token = f"mock:{shared_email}"

    db = SessionLocal()
    try:
        # Seed account A under subject S1 with the shared email.
        account_a = Account(
            id=uuid.uuid4(),
            auth_user_id=s1_subject_uuid,
            email=shared_email,
            display_name="Account A (subject S1)",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(account_a)
        db.commit()
        a_id = account_a.id
        a_auth_user_id = account_a.auth_user_id

        client = TestClient(app)
        r = client.post(
            "/auth/session/init",
            headers={"Authorization": f"Bearer {s2_email_token}"},
        )
        assert r.status_code == 200, r.text
        b_account_id = uuid.UUID(r.json()["account_id"])

        # Two distinct rows now coexist with the same email.
        assert b_account_id != a_id, "S2 must materialize a NEW row, not S1's"

        # Account A is unchanged — no relink, no soft-delete.
        db.expire_all()
        refreshed_a = db.query(Account).filter(Account.id == a_id).one_or_none()
        assert refreshed_a is not None
        assert refreshed_a.auth_user_id == a_auth_user_id, (
            "Forbidden: account A's auth_user_id was rewritten (silent "
            "ownership transfer to S2)."
        )
        assert (
            refreshed_a.deleted_at is None
        ), "Forbidden: account A was soft-deleted as a side effect."
        assert refreshed_a.email == shared_email
    finally:
        # Cleanup: best-effort delete of both rows.
        try:
            db.query(Account).filter(Account.email == shared_email).delete()
            db.commit()
        except Exception:
            db.rollback()
        db.close()


# ---------------------------------------------------------------------------
# H. Hygiene & observability
# ---------------------------------------------------------------------------


@pytest.mark.xfail(strict=True, reason="redesign-pending: T-H1")
def test_T_H1_no_credential_prefix_in_logs() -> None:
    """T-H1 — Inspect logs for credential leakage.

    Action:
        Across all environments, capture log output during
        authenticated request flows.

    Expected:
        Zero log lines containing any prefix of any token, header, or
        cookie value.

    Forbidden:
        Any DIAG_AUTHZ_HEADER-style leakage; any redaction-by-truncation
        that still emits a non-empty prefix.

    Validates: B10
    Prevents:  F10
    """
    raise NotImplementedError


@pytest.mark.xfail(strict=True, reason="redesign-pending: T-H2")
def test_T_H2_at_most_one_whoami_per_boot() -> None:
    """T-H2 — Inspect mounted components for duplicate auth-state
    network calls.

    Action:
        Boot the app and observe the count of whoami-equivalent calls.

    Expected:
        At most one whoami-equivalent call per boot.

    Forbidden:
        NavBar (or any other component) issuing its own whoami; any
        component reading auth state by network call instead of from
        the single owner.

    Validates: B1, T7 ; I-G
    Prevents:  F8, audit §17 duplicate whoami
    """
    raise NotImplementedError


@_requires_postgres
def test_T_H3_read_endpoints_perform_no_writes() -> None:
    """T-H3 — Inspect the read endpoint for write effects.

    Action:
        Exercise GET /auth/session (the read-only resolver from the
        redesign) for a token whose account row does NOT yet exist.
        Attach a SQL-statement listener to the engine and assert that
        no INSERT/UPDATE/DELETE statement is emitted.

    Expected:
        Status 200 with `materialized=False`; zero DML statements
        emitted (B4, I-B). The verifier touches no DB; the route
        performs a single SELECT.

    Forbidden:
        Any INSERT/UPDATE/DELETE; any side effect that materializes a
        new row from the read path itself.

    Validates: B4, T6 ; I-B
    Prevents:  FC1 commit-on-read
    """
    from backend.core.database import engine

    # Use a token whose subject has no row yet. Mock derives auth_user_id
    # deterministically from email, so a fresh email guarantees no row.
    fresh_email = f"t-h3-fresh-{uuid.uuid4().hex[:8]}@example.test"
    token = f"mock:{fresh_email}"

    dml_statements: list[str] = []

    def _on_before_execute(
        conn, clauseelement, multiparams, params, execution_options
    ):  # noqa: ARG001
        try:
            text = str(clauseelement).strip().upper()
        except Exception:
            return
        # The SQLAlchemy event fires for every statement, including
        # SAVEPOINTs and transaction control. We're only interested in
        # DML targeting the accounts table.
        if text.startswith(("INSERT", "UPDATE", "DELETE")) and "ACCOUNTS" in text:
            dml_statements.append(text[:200])

    event.listen(engine, "before_execute", _on_before_execute)
    try:
        client = TestClient(app)
        r = client.get(
            "/auth/session",
            headers={"Authorization": f"Bearer {token}"},
        )
    finally:
        event.remove(engine, "before_execute", _on_before_execute)

    assert r.status_code == 200, r.text
    body = r.json()
    assert body["materialized"] is False, body
    assert body["account_id"] is None

    assert (
        not dml_statements
    ), "Forbidden DML emitted by /auth/session (B4 violation):\n" + "\n".join(
        dml_statements
    )
