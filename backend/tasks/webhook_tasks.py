"""Celery tasks for deferred background work.

Sprint 27 H4:
  - process_stripe_webhook
  - export_telemetry_csv
  - cleanup_deleted_accounts
"""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session as DbSession

from backend.core.database import SessionLocal
from backend.models.billing import ProcessedWebhookEvent
from backend.services.webhook_handler import process_event
from backend.tasks.celery_app import app

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=3, default_retry_delay=10)
def process_stripe_webhook(self, event_id: str, event_type: str, payload: dict) -> str:
    """Deferred Stripe webhook processing.

    Called from billing.py:stripe_webhook instead of inline processing.
    Retries on failure up to 3 times with 10s backoff.
    """
    db: DbSession = SessionLocal()
    try:
        from backend.services.payment_provider import WebhookEvent

        event = WebhookEvent(
            event_id=event_id,
            event_type=event_type,
            payload=payload,
        )
        # Dedup check before processing
        existing = (
            db.query(ProcessedWebhookEvent)
            .filter(ProcessedWebhookEvent.event_id == event_id)
            .one_or_none()
        )
        if existing is not None:
            return "duplicate"

        outcome = process_event(db, event)
        db.commit()
        return outcome
    except Exception as exc:
        db.rollback()
        logger.exception("webhook_task_failed event_id=%s", event_id)
        raise self.retry(exc=exc)
    finally:
        db.close()


@app.task(bind=True, max_retries=2, default_retry_delay=30)
def export_telemetry_csv(self, start_date: str, end_date: str, admin_email: str) -> str:
    """Deferred telemetry CSV export."""
    # TODO: implement actual export + email delivery
    logger.info(
        "telemetry_export_task start=%s end=%s admin=%s",
        start_date,
        end_date,
        admin_email,
    )
    return "not_implemented"


@app.task(bind=True, max_retries=2, default_retry_delay=60)
def cleanup_deleted_accounts(self) -> str:
    """Periodic cleanup of accounts past grace period."""
    # TODO: implement hard deletion after grace period
    logger.info("cleanup_deleted_accounts_task")
    return "not_implemented"
