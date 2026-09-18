"""Learner help-request models — the "Call me" callback.

Single-purpose schema for POST /api/v1/help/callback. US/CA only —
the toll-free line's outbound trunk and the product's service area
are North American, and opening arbitrary international dialing is
a toll-fraud vector.
"""

import re

from pydantic import BaseModel, Field, field_validator

_E164_US_CA = re.compile(r"^\+1[2-9]\d{9}$")


class CallbackRequest(BaseModel):
    """A learner asking for a callback.

    `context` is optional free text ("what are you stuck on") — kept
    short and never required, per the articulation-barrier finding in
    the learner-help research memo.
    """

    phone: str = Field(min_length=7, max_length=20)
    context: str | None = Field(default=None, max_length=300)
    website: str | None = None

    @field_validator("phone")
    @classmethod
    def _phone_us_ca(cls, value: str) -> str:
        digits = re.sub(r"[^\d]", "", value)
        if len(digits) == 10:
            digits = "1" + digits
        e164 = "+" + digits
        if not _E164_US_CA.match(e164):
            raise ValueError("US or Canada phone number required")
        return e164


class CallbackResponse(BaseModel):
    status: str
    calling: bool
