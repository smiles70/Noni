"""Gift token issuance and redemption.

See ADR 0021 and `docs/architecture/SCHEMA.md`.

The plaintext token is returned ONCE (in the checkout success response
and any receipt/confirmation email). The DB stores only the SHA-256
hash; the row's `gift_claim_token_hash` column is unique.
"""

from __future__ import annotations

import base64
import hashlib
import secrets
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session as DbSession

from backend.models.accounts import Account
from backend.models.billing import Purchase
from backend.services import entitlements


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def issue_token(db: DbSession, purchase: Purchase) -> str:
    """Generate, hash, persist; return the plaintext token to the caller.

    Returned exactly once; not retrievable afterwards.
    """
    raw = base64.urlsafe_b64encode(secrets.token_bytes(24)).rstrip(b"=").decode("ascii")
    purchase.gift_claim_token_hash = _hash(raw)
    db.flush()
    return raw


def hash_token(raw: str) -> str:
    """Public helper exposed for tests / admin tooling."""
    return _hash(raw)


def _hash(raw: str) -> str:
    return hashlib.sha256(raw.encode("ascii")).hexdigest()


class GiftClaimError(Exception):
    """Raised on any failure path during redemption. Caller maps to envelope."""


def claim(
    db: DbSession,
    *,
    raw_token: str,
    beneficiary_account: Account,
) -> Purchase:
    """Redeem a gift token for the beneficiary.

    Side effects (single transaction; caller commits):
      - Sets `purchase.beneficiary_account_id`
      - Stamps `purchase.gift_claimed_at`
      - Clears `purchase.gift_claim_token_hash` (single-use)
      - Grants entitlement to the beneficiary
    """
    if not raw_token:
        raise GiftClaimError("empty_token")

    token_hash = _hash(raw_token)
    purchase = (
        db.query(Purchase)
        .filter(Purchase.gift_claim_token_hash == token_hash)
        .one_or_none()
    )
    if purchase is None:
        raise GiftClaimError("not_found")
    if purchase.status != "paid":
        raise GiftClaimError(f"unpaid_purchase:{purchase.status}")
    if purchase.gift_claimed_at is not None:
        raise GiftClaimError("already_claimed")
    if purchase.refunded_at is not None:
        raise GiftClaimError("refunded")

    purchase.beneficiary_account_id = beneficiary_account.id
    purchase.gift_claimed_at = _utcnow()
    purchase.gift_claim_token_hash = None  # single-use

    entitlements.grant(
        db,
        account_id=beneficiary_account.id,
        product_code=purchase.product_code,
        granted_by_purchase_id=purchase.id,
    )
    db.flush()
    return purchase


def lookup_for_redemption(db: DbSession, raw_token: str) -> Optional[Purchase]:
    """Read-only lookup used by the redemption preview page.

    Returns None if the token doesn't match a redeemable row.
    """
    token_hash = _hash(raw_token)
    purchase = (
        db.query(Purchase)
        .filter(Purchase.gift_claim_token_hash == token_hash)
        .one_or_none()
    )
    if purchase is None:
        return None
    if purchase.status != "paid":
        return None
    if purchase.gift_claimed_at is not None:
        return None
    if purchase.refunded_at is not None:
        return None
    return purchase


def _unused() -> uuid.UUID:
    """Placeholder to make linter happy about uuid import (used by callers)."""
    return uuid.uuid4()
