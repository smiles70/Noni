"""Deferred email sends — never in the request path."""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session as DbSession

from backend.core.config import settings
from backend.core.database import SessionLocal
from backend.models.accounts import Account
from backend.models.billing import Purchase
from backend.services import email
from backend.tasks.celery_app import app

logger = logging.getLogger(__name__)


def _buyer_email(db: DbSession, purchase: Purchase) -> str | None:
    buyer = (
        db.query(Account)
        .filter(Account.id == purchase.buyer_account_id)
        .one_or_none()
    )
    return buyer.email if buyer else None


@app.task(bind=True, max_retries=3, default_retry_delay=30)
def send_gift_receipt(self, purchase_id: str) -> str:
    """Receipt + shareable redeem link to the gift giver (post-payment)."""
    db: DbSession = SessionLocal()
    try:
        purchase = db.query(Purchase).filter(Purchase.id == purchase_id).one_or_none()
        if purchase is None:
            return "noop"
        to = _buyer_email(db, purchase)
        if not to:
            return "noop"
        url = f"{settings.FRONTEND_URL}/gift-redeem"
        return "sent" if email.send_gift_receipt(to, url) else "failed"
    finally:
        db.close()


@app.task(bind=True, max_retries=3, default_retry_delay=30)
def send_gift_claimed(self, purchase_id: str) -> str:
    """Notify the giver that the gift was accepted."""
    db: DbSession = SessionLocal()
    try:
        purchase = db.query(Purchase).filter(Purchase.id == purchase_id).one_or_none()
        if purchase is None or purchase.gift_claimed_at is None:
            return "noop"
        to = _buyer_email(db, purchase)
        if not to:
            return "noop"
        return "sent" if email.send_gift_claimed(to) else "failed"
    finally:
        db.close()
