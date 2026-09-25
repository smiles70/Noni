"""Retell outbound-call client — the "Call me" callback lane.

POST /v2/create-phone-call dials the learner from the toll-free line
with the dedicated callback agent (outbound-framed prompt; see
retell/prompts/callback-v1.md in the retell repo). Capability-off by
default: an unset key or agent id means "we can't call", and callers
must treat that as a normal state, never an exception.
"""

import logging
import time

import httpx

from backend.core.config import settings

log = logging.getLogger(__name__)

RETELL_BASE = "https://api.retellai.com"
_TIMEOUT = 10.0


def callback_available() -> bool:
    return bool(settings.RETELL_API_KEY and settings.RETELL_CALLBACK_AGENT_ID)


def create_callback(phone_e164: str) -> str | None:
    """Dial `phone_e164` from the toll-free line via the callback agent.

    Returns the Retell call_id on success, None on any failure —
    the caller decides how to degrade; a failed dial is an ops signal,
    not a user-facing error.
    """
    if not callback_available():
        log.warning("retell_callback_unconfigured")
        return None
    try:
        payload: dict[str, str] = {
            "from_number": settings.RETELL_FROM_NUMBER,
            "to_number": phone_e164,
            "override_agent_id": settings.RETELL_CALLBACK_AGENT_ID,
        }
        if settings.CRM_API_URL:
            payload["webhook_url"] = (
                f"{settings.CRM_API_URL.rstrip('/')}/api/retell/webhook"
            )
        resp = httpx.post(
            f"{RETELL_BASE}/v2/create-phone-call",
            json=payload,
            headers={"Authorization": f"Bearer {settings.RETELL_API_KEY}"},
            timeout=_TIMEOUT,
        )
    except httpx.HTTPError as exc:
        log.error("retell_callback_transport_error", extra={"error": str(exc)})
        return None
    if resp.status_code not in (200, 201):
        log.error(
            "retell_callback_rejected",
            extra={"status": resp.status_code, "body": resp.text[:200]},
        )
        return None
    return resp.json().get("call_id")


def file_help_contact(phone_e164: str, context: str | None, email: str | None) -> None:
    """File the callback request in the CRM as a form_submit event.

    The CRM's tracking intake files a Contact from `mail`/`phone`-keyed
    fields; `path=/curriculum/help` marks the event as a help request so
    downstream alerts can tag it `[help]`, not `[form]`. Fire-and-forget:
    a CRM outage must never break the callback path.
    """
    if not (settings.CRM_API_URL and settings.CRM_SITE_ID):
        return
    fields: dict[str, str] = {
        "phone": phone_e164,
        "help_request": context or "callback",
    }
    if email:
        fields["email"] = email
    try:
        httpx.post(
            f"{settings.CRM_API_URL.rstrip('/')}/api/t/e",
            headers={"Origin": "https://www.mynaani.com"},
            json={
                "siteId": settings.CRM_SITE_ID,
                "visitorId": f"help-{phone_e164[-4:]}",
                "events": [
                    {
                        "type": "form_submit",
                        "host": "www.mynaani.com",
                        "path": "/curriculum/help",
                        "at": int(time.time() * 1000),
                        "fields": fields,
                    }
                ],
            },
            timeout=5.0,
        )
    except httpx.HTTPError as exc:
        log.warning("crm_help_contact_failed", extra={"error": str(exc)})
