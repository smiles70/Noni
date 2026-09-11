"""Celery tasks for n8n help request delivery."""

from __future__ import annotations

import logging

import httpx
from sqlalchemy.orm import Session as DbSession

from backend.core.config import settings
from backend.core.database import SessionLocal
from backend.models.support_request import SupportRequest, SupportRequestAudit
from backend.tasks.celery_app import app

logger = logging.getLogger(__name__)


def _is_retryable(exc: Exception) -> bool:
    """Only retry transient errors. 4xx/validation failures are terminal."""
    if isinstance(exc, httpx.TimeoutException):
        return True
    if isinstance(exc, httpx.ConnectError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in (408, 429, 500, 502, 503, 504)
    return False


@app.task(bind=True, max_retries=3, default_retry_delay=10)
def deliver_help_request_to_n8n(self, support_request_id: str) -> str:
    """Post the persisted help request to the configured n8n webhook."""
    db: DbSession = SessionLocal()
    try:
        request = (
            db.query(SupportRequest)
            .filter(SupportRequest.id == support_request_id)
            .one_or_none()
        )
        if request is None:
            logger.warning("help_request_not_found id=%s", support_request_id)
            return "not_found"

        webhook_url = getattr(settings, "N8N_WEBHOOK_URL", None)
        if not webhook_url:
            logger.info("n8n_webhook_not_configured id=%s", support_request_id)
            request.status = "n8n_failed"
            request.n8n_response_code = 0
            request.n8n_response_text = "n8n not configured"
            db.add(
                SupportRequestAudit(
                    support_request_id=request.id,
                    action="n8n_not_configured",
                    detail="N8N_WEBHOOK_URL is empty",
                )
            )
            db.commit()
            return "not_configured"

        payload = {
            "request_id": request.request_id,
            "context": request.context,
            "category": request.category,
            "email": request.email,
            "message": request.message,
            "page_path": request.page_path,
            "ip_address": request.ip_address,
            "created_at": request.created_at.isoformat() if request.created_at else None,
        }

        headers = {"Content-Type": "application/json"}
        token = getattr(settings, "N8N_WEBHOOK_TOKEN", None)
        if token:
            headers["X-N8N-Auth"] = token

        try:
            resp = httpx.post(
                webhook_url,
                json=payload,
                headers=headers,
                timeout=10,
                follow_redirects=False,
            )
            request.n8n_response_code = resp.status_code
            request.n8n_response_text = resp.text[:2000]
            resp.raise_for_status()
            request.status = "n8n_delivered"
            db.add(
                SupportRequestAudit(
                    support_request_id=request.id,
                    action="n8n_delivered",
                    detail=f"status={resp.status_code}",
                )
            )
            db.commit()
            return "delivered"
        except httpx.HTTPError as exc:
            request.status = "n8n_failed"
            db.add(
                SupportRequestAudit(
                    support_request_id=request.id,
                    action="n8n_failed",
                    detail=str(exc)[:512],
                )
            )
            db.commit()
            if _is_retryable(exc) and self.request.retries < self.max_retries:
                raise self.retry(exc=exc)
            logger.exception("n8n_delivery_failed id=%s", support_request_id)
            return "failed"
    finally:
        db.close()
