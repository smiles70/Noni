"""Contact inquiry — general "Talk to us" form payload (/contact).

Intake: .ai/intake/2026-09-17-p2-contact-page-talk-to-us.md
"""

import re

from pydantic import BaseModel, Field, field_validator

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ContactInquiry(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    email: str = Field(min_length=3, max_length=254)
    phone: str = Field(default="", max_length=40)
    # Honeypot: bots fill it, humans never see it.
    website: str = Field(default="", max_length=80)

    @field_validator("email")
    @classmethod
    def _email_shape(cls, v: str) -> str:
        if not _EMAIL_RE.match(v):
            raise ValueError("Please enter a valid email address.")
        return v


def render_contact(inq: ContactInquiry) -> str:
    """Plain-text body sent to the help inbox."""
    return "\n".join(
        [
            f"Name: {inq.first_name} {inq.last_name}",
            f"Email: {inq.email}",
            f"Phone: {inq.phone or 'Not provided'}",
        ]
    )
