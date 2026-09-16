"""Site-chrome API — backend-served footer content.

Single endpoint: `/footer` returns the shared footer copy (nav row,
legal row, landing mini-strip) so every surface renders identical
labels. Pure read; no auth. See `.ai/intake/2026-09-16-p2-*`.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks
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
