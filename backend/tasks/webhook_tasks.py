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
def cleanup_deleted_accounts(self) -> dict:
    """Daily: execute GDPR deletion for requests past their grace period.

    Safety envelope:
      - only `status='requested' AND scheduled_for <= now` rows
      - per-request commit isolation: one failure doesn't block the rest
      - idempotent by construction (status flips to 'completed')
      - logs counts only — never PII
    """
    from datetime import datetime, timezone

    from backend.models.accounts import Account
    from backend.models.governance import DeletionRequest
    from backend.services.deletion import execute_deletion

    db = SessionLocal()
    now = datetime.now(timezone.utc)
    done, failed = 0, 0
    try:
        due = (
            db.query(DeletionRequest)
            .filter(
                DeletionRequest.status == "requested",
                DeletionRequest.scheduled_for <= now,
            )
            .all()
        )
        for req in due:
            try:
                account = db.query(Account).filter(Account.id == req.account_id).first()
                if account is not None:
                    execute_deletion(db, account)
                    db.commit()
                    done += 1
            except Exception:  # noqa: BLE001 — isolate, log id only
                db.rollback()
                failed += 1
                logger.error("deletion_execute_failed request_id=%s", req.id)
        logger.info("deletion_sweep done=%d failed=%d due=%d", done, failed, len(due))
        return {"done": done, "failed": failed, "due": len(due)}
    finally:
        db.close()
