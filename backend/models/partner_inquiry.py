"""Partner inquiry — public contact form payload.

Intake: .ai/intake/2026-09-16-p2-backend-partner-inquiry-email.md
"""

import re

from pydantic import BaseModel, Field, field_validator

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class PartnerInquiry(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    email: str = Field(min_length=3, max_length=254)
    phone: str = Field(default="", max_length=40)
    organization: str = Field(min_length=1, max_length=160)
    organization_type: str = Field(default="", max_length=80)
    role: str = Field(default="", max_length=80)
    message: str = Field(default="", max_length=4000)
    # Honeypot: bots fill it, humans never see it. Any non-empty
    # value is rejected before any email is sent.
    website: str = Field(default="", max_length=80)

    @field_validator("email")
    @classmethod
    def _email_shape(cls, v: str) -> str:
        if not _EMAIL_RE.match(v):
            raise ValueError("Please enter a valid email address.")
        return v


class PartnerInquiryReceipt(BaseModel):
    status: str
    delivered: bool


def render_inquiry(inq: PartnerInquiry) -> str:
    """Plain-text body sent to the partnership inbox."""
    org_type = inq.organization_type or "Not specified"
    lines = [
        f"Name: {inq.first_name} {inq.last_name}",
        f"Email: {inq.email}",
        f"Phone: {inq.phone or 'Not provided'}",
        f"Organization: {inq.organization}",
        f"Organization type: {org_type}",
        f"Role: {inq.role or 'Not specified'}",
        "",
        "Message:",
        inq.message or "(none)",
    ]
    return "\n".join(lines)
