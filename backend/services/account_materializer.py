"""Stage 2 — account materialization (B4, B7, B8, I-D, I-E, T6).

Source:
    docs/design/login-redesign-2026-05-17.md §2.4, §6.2-§6.4.
    docs/audits/login-system-constraints-2026-05-17.md §3.5.
    Frozen reference tag: login-redesign-v1.

This is the ONLY writer of `accounts` rows in the redesigned login
path. It is invoked exclusively from `POST /auth/session/init`, which
is a write event triggered by the frontend on first-sight sign-in.
GET endpoints (e.g. /auth/session) never call it (B4).

Constraints anchored:
    B4   write occurs only on the init endpoint, never on a read.
    B7   deleted accounts cannot be silently resurrected; lookup
         filters `deleted_at IS NULL`, and a soft-deleted row blocks
         materialization with `auth.account_deleted`.
    B8   one subject ↔ one row, monotonic; ON CONFLICT keys on
         `auth_user_id` only. No email-relink branch exists.
    I-D  subject→row mapping is append-only / immutable.
    I-E  deletion is terminal until an explicit re-create call.
    T6   materialization is a single write event.

Telemetry: every attempt emits `account_materialize_attempts_total{
result=success|conflict|deleted}` and email-collision detections emit
`email_collision_observed_total` (B5 envelope is emitted by the route,
not here).
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session as DbSession

from backend.app.telemetry import (
    record_email_collision,
    record_materialize_attempt,
)
from backend.models.accounts import Account
from backend.services.auth_provider import AuthClaims
from backend.services.auth_verifier import AuthError

logger = logging.getLogger("noni.account_materializer")


def materialize(db: DbSession, claims: AuthClaims) -> Account:
    """Idempotent first-sight materialization for the given claims.

    Behaviour:
      1. INSERT ... ON CONFLICT (auth_user_id) DO NOTHING.
      2. SELECT the row (the insert may have been a no-op).
      3. If the row's `deleted_at` is set → raise
         AuthError("auth.account_deleted"). Caller turns this into a
         401 envelope; the frontend renders the deleted-account surface
         and only `/me/recreate` can clear `deleted_at` (B7, I-E).
      4. Otherwise return the row.

    Email collisions (a row exists with the same email but a different
    `auth_user_id`) are observed via a side-channel counter but DO NOT
    cause a relink — there is no UPDATE-of-auth_user_id branch (B8,
    I-D). M1 dropped the UNIQUE constraint on email so the new row
    inserts cleanly alongside any existing row with the same email.

    The caller is responsible for `db.commit()`. We do not commit here
    so the route handler controls transaction boundaries.
    """
    now = datetime.now(timezone.utc)

    # Step 1: idempotent insert keyed on auth_user_id (B8).
    stmt = (
        pg_insert(Account)
        .values(
            id=uuid.uuid4(),
            auth_user_id=claims.auth_user_id,
            email=claims.email,  # may be NULL post-M1 (B12)
            display_name=claims.display_name,
            created_at=now,
            updated_at=now,
        )
        .on_conflict_do_nothing(constraint="uq_accounts_auth_user_id")
    )
    db.execute(stmt)
    db.flush()

    # Step 2: resolve the row (insert may have been a no-op on a race).
    account = (
        db.query(Account)
        .filter(Account.auth_user_id == claims.auth_user_id)
        .one_or_none()
    )
    if account is None:
        # Should be unreachable: either insert succeeded or a conflicting
        # row exists. Surface as transient so we don't blame the user.
        record_materialize_attempt("conflict")
        logger.error(
            "materialize_no_row_after_insert auth_user_id=%s",
            claims.auth_user_id,
        )
        raise AuthError("auth.transient_db_unavailable")

    # Step 3: terminal-deletion gate (B7, I-E).
    if account.deleted_at is not None:
        record_materialize_attempt("deleted")
        raise AuthError("auth.account_deleted")

    # Step 4: email-collision observability (B8 / FC3 prevention).
    # If another row carries the same email under a different subject,
    # we structurally cannot leak it (no relink), but we count the
    # observation so ops can spot impersonation attempts. Email may be
    # NULL post-M1; in that case skip the check.
    if claims.email:
        other = (
            db.query(Account.id)
            .filter(
                Account.email == claims.email,
                Account.auth_user_id != claims.auth_user_id,
                Account.deleted_at.is_(None),
            )
            .first()
        )
        if other is not None:
            record_email_collision()
            logger.info(
                "email_collision_observed auth_user_id=%s",
                claims.auth_user_id,
            )

    record_materialize_attempt("success")
    return account
