"""GDPR-style account deletion.

See ADR 0023 and ADR 0024.

Two-phase:
  1. User requests deletion → `deletion_requests` row with `status=requested`
     and `scheduled_for = now() + grace`. Account is soft-deleted
     (`accounts.deleted_at`) but data is retained for the grace period
     so the user can cancel.
  2. After the grace period, an operator (or scheduled job) calls
     `execute_deletion` to zero PII and mark the request complete.
     Audit-bearing rows (purchases, entitlements,
     processed_webhook_events) are retained anonymized.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session as DbSession

from backend.core.config import settings
from backend.models.accounts import Account
from backend.models.auth import Session as SessionRow
from backend.models.governance import DeletionRequest


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def request_deletion(
    db: DbSession, account: Account, *, grace_days: Optional[int] = None
) -> DeletionRequest:
    """Create a pending DeletionRequest and soft-delete the account."""
    grace = (
        grace_days if grace_days is not None else settings.DELETION_GRACE_PERIOD_DAYS
    )

    # Reuse any existing pending request rather than creating a duplicate.
    existing = (
        db.query(DeletionRequest)
        .filter(
            DeletionRequest.account_id == account.id,
            DeletionRequest.status == "requested",
        )
        .one_or_none()
    )
    if existing is not None:
        return existing

    req = DeletionRequest(
        id=uuid.uuid4(),
        account_id=account.id,
        scheduled_for=_utcnow() + timedelta(days=grace),
        status="requested",
    )
    db.add(req)
    account.deleted_at = _utcnow()
    # Revoke all active sessions immediately on deletion request.
    db.query(SessionRow).filter(
        SessionRow.account_id == account.id,
        SessionRow.revoked_at.is_(None),
    ).update(
        {"revoked_at": _utcnow(), "revocation_reason": "deletion_requested"},
        synchronize_session=False,
    )
    db.flush()
    return req


def cancel_deletion(db: DbSession, account: Account) -> Optional[DeletionRequest]:
    """Cancel a pending deletion request (during the grace period)."""
    req = (
        db.query(DeletionRequest)
        .filter(
            DeletionRequest.account_id == account.id,
            DeletionRequest.status == "requested",
        )
        .one_or_none()
    )
    if req is None:
        return None
    if _utcnow() > req.scheduled_for:
        return None  # Past grace; cannot cancel.
    req.status = "cancelled"
    req.completed_at = _utcnow()
    account.deleted_at = None
    db.flush()
    return req


def execute_deletion(db: DbSession, account: Account) -> Optional[DeletionRequest]:
    """Zero PII on the account and mark the request complete.

    Audit-bearing tables (purchases, entitlements, processed_webhook_events,
    telemetry_events) are intentionally left in place; they reference the
    account by UUID but no longer link to identifying information.
    """
    req = (
        db.query(DeletionRequest)
        .filter(
            DeletionRequest.account_id == account.id,
            DeletionRequest.status == "requested",
        )
        .one_or_none()
    )
    if req is None:
        return None

    # Zero PII. Email is required NOT NULL so we replace with an opaque tombstone.
    account.email = f"deleted+{account.id}@example.invalid"
    account.display_name = None
    account.auth_user_id = None
    account.deleted_at = _utcnow()

    req.status = "completed"
    req.completed_at = _utcnow()
    db.flush()
    return req
