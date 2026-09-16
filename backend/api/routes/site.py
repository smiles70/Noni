"""Site-chrome API — backend-served footer content.

Single endpoint: `/footer` returns the shared footer copy (nav row,
legal row, landing mini-strip) so every surface renders identical
labels. Pure read; no auth. See `.ai/intake/2026-09-16-p2-*`.
"""

import hashlib
import hmac
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import JSONResponse

from backend.content.site_chrome import SITE_FOOTER_CONTENT
from backend.core.config import settings
from backend.models.partner_inquiry import (
    PartnerInquiry,
    PartnerInquiryReceipt,
    render_inquiry,
)
from backend.models.site_chrome import SiteFooterContent
from backend.services import email

router = APIRouter()


@router.get("/footer", response_model=SiteFooterContent)
def get_footer() -> JSONResponse:
    """Return the shared footer copy with the current copyright year."""
    payload = dict(SITE_FOOTER_CONTENT)
    payload["copyright"] = (
        f"© {datetime.now(timezone.utc).year} mynaani. All rights reserved."
    )
    payload["contact_phone"] = settings.PARTNER_PHONE
    content = SiteFooterContent.model_validate(payload)
    resp = JSONResponse(content=content.model_dump())
    resp.headers["Cache-Control"] = "public, max-age=300"
    return resp


@router.post("/partner-inquiry", response_model=PartnerInquiryReceipt)
def submit_partner_inquiry(
    inquiry: PartnerInquiry, background: BackgroundTasks
) -> PartnerInquiryReceipt:
    """Accept a /partners form submission.

    Honeypot rejects bots silently with a synthetic receipt so the
    response surface never reveals which fields tripped the check.
    Real submissions are handed to the email service off the request
    path — the caller gets an immediate receipt either way.
    """
    if inquiry.website:
        return PartnerInquiryReceipt(status="received", delivered=False)
    subject = f"Partner inquiry — {inquiry.organization}"
    body = render_inquiry(inquiry)
    background.add_task(email.send, settings.PARTNER_INBOX, subject, body)
    return PartnerInquiryReceipt(status="received", delivered=True)


def _verify_retell_signature(raw: bytes, signature: str) -> bool:
    """HMAC-SHA256 of the raw request body, keyed by the account API key.

    When RETELL_API_KEY is unset we can't verify — accept and rely on the
    same honeypot/validation the public form path uses (the payload shape
    is the only difference). Log so ops knows the check is inactive.
    """
    if not settings.RETELL_API_KEY:
        return True
    expected = hmac.new(
        settings.RETELL_API_KEY.encode(), raw, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/retell/partner-inquiry")
async def retell_partner_inquiry(
    request: Request, background: BackgroundTasks
) -> JSONResponse:
    """Adapter for the Retell facility agent's `submit_partner_inquiry`
    custom tool (see retell/tools/submit-partner-inquiry.json).

    Retell POSTs {name, args, chat} (chat agents) or {name, args, call}
    (voice). We unwrap args into the same PartnerInquiry validation as
    the public form and answer with a short line the agent can say back.
    """
    raw = await request.body()
    signature = request.headers.get("x-retell-signature", "")
    if not _verify_retell_signature(raw, signature):
        return JSONResponse(
            status_code=401,
            content={"result": "I could not verify that request."},
        )
    payload = await request.json()
    if payload.get("name") != "submit_partner_inquiry":
        return JSONResponse(
            status_code=400,
            content={"result": "Unknown tool call."},
        )
    try:
        inquiry = PartnerInquiry.model_validate(payload.get("args") or {})
    except Exception:
        return JSONResponse(
            status_code=422,
            content={
                "result": (
                    "I am missing some details. Let me collect the "
                    "required fields and try again."
                )
            },
        )
    if inquiry.website:
        return JSONResponse(
            content={"result": "Thank you, your inquiry has been noted."}
        )
    subject = f"Partner inquiry — {inquiry.organization}"
    background.add_task(
        email.send,
        settings.PARTNER_INBOX,
        subject,
        render_inquiry(inquiry),
    )
    return JSONResponse(
        content={
            "result": (
                "Thank you — I have sent your details to our partnership "
                "team and someone will follow up with you."
            )
        }
    )
