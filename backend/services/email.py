"""Transactional email via Resend.

Design contract (gift lifecycle, intake 2026-09-06):
  - Sending must NEVER break a purchase or claim: every public call
    swallows errors and returns False on failure.
  - No API key configured => log-and-noop (staging/dev safe).
  - Copy is geragogy-bound: plain words, no urgency, no exclamation.
"""

from __future__ import annotations

import logging

import httpx

from backend.core.config import settings

logger = logging.getLogger(__name__)

_RESEND_URL = "https://api.resend.com/emails"


def send(to: str, subject: str, text: str) -> bool:
    """Send a plain-text email. Returns True on provider acceptance.

    Fails quiet: logs and returns False; never raises.
    """
    if settings.EMAIL_OVERRIDE_TO:
        to = settings.EMAIL_OVERRIDE_TO
    if not settings.RESEND_API_KEY:
        logger.info("email skipped (no RESEND_API_KEY): %s", subject)
        return False
    try:
        resp = httpx.post(
            _RESEND_URL,
            headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
            json={
                "from": settings.EMAIL_FROM,
                "to": [to],
                "subject": subject,
                "text": text,
            },
            timeout=10,
        )
        if resp.status_code in (200, 201):
            return True
        logger.warning("email rejected %s: %s", resp.status_code, resp.text[:200])
        return False
    except Exception:
        logger.exception("email send failed")
        return False


def send_gift_receipt(buyer_email: str, redeem_url: str) -> bool:
    """Receipt + shareable link to the gift giver."""
    text = (
        "Thank you for your gift.\n\n"
        "Here is the page where they will enter the gift token you received "
        "at checkout — share both, however is easiest: forward this email, "
        "read it aloud, or write it on a card.\n\n"
        f"{redeem_url}\n\n"
        "When they open it, they will see the gift before accepting it. "
        "No card or payment is ever asked of them.\n\n"
        "We will let you know when it is accepted.\n\n"
        "— mynaani"
    )
    return send(buyer_email, "Your gift is ready to share", text)


def send_gift_claimed(buyer_email: str) -> bool:
    """Claim notification back to the giver."""
    text = (
        "Good news — your gift was accepted.\n\n"
        "They now have the full program, and there is nothing more for you "
        "to do.\n\n"
        "Thank you for sharing it.\n\n"
        "— mynaani"
    )
    return send(buyer_email, "Your gift was accepted", text)
