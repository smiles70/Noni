"""Entitlement service.

See `docs/architecture/SCHEMA.md` and ADR 0021.

Invariants:
- Grants are idempotent on (account_id, product_code).
- Refunds set `revoked_at`; rows are NEVER deleted (audit retention).
- `content_version` is snapshotted at grant time; a learner keeps the
  content they paid for even if the product is later versioned.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session as DbSession

from backend.models.billing import Entitlement, Product


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def grant(
    db: DbSession,
    *,
    account_id: uuid.UUID,
    product_code: str,
    granted_by_purchase_id: uuid.UUID,
    content_version: Optional[int] = None,
) -> Entitlement:
    """Grant or re-activate an entitlement.

    If a revoked row exists, re-activate it (clear `revoked_at`,
    update `granted_by_purchase_id`). If an active row exists, return
    it unchanged (idempotent).
    """
    existing = (
        db.query(Entitlement)
        .filter(
            Entitlement.account_id == account_id,
            Entitlement.product_code == product_code,
        )
        .one_or_none()
    )
    if existing is not None:
        if existing.revoked_at is not None:
            existing.revoked_at = None
            existing.revocation_reason = None
            existing.granted_by_purchase_id = granted_by_purchase_id
            existing.granted_at = _utcnow()
        return existing

    if content_version is None:
        product = db.query(Product).filter(Product.code == product_code).one_or_none()
        if product is None:
            raise ValueError(f"unknown product_code: {product_code}")
        content_version = product.content_version

    row = Entitlement(
        account_id=account_id,
        product_code=product_code,
        granted_by_purchase_id=granted_by_purchase_id,
        content_version=content_version,
    )
    db.add(row)
    db.flush()
    return row


def revoke(
    db: DbSession,
    *,
    account_id: uuid.UUID,
    product_code: str,
    reason: str = "refund",
) -> Optional[Entitlement]:
    row = (
        db.query(Entitlement)
        .filter(
            Entitlement.account_id == account_id,
            Entitlement.product_code == product_code,
        )
        .one_or_none()
    )
    if row is None:
        return None
    if row.revoked_at is not None:
        return row  # already revoked
    row.revoked_at = _utcnow()
    row.revocation_reason = reason
    db.flush()
    return row


def has_active(db: DbSession, account_id: uuid.UUID, product_code: str) -> bool:
    row = (
        db.query(Entitlement)
        .filter(
            Entitlement.account_id == account_id,
            Entitlement.product_code == product_code,
            Entitlement.revoked_at.is_(None),
        )
        .one_or_none()
    )
    return row is not None
