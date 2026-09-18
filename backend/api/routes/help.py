"""Learner help API — the "Call me" callback (learner-help-channel intake).

POST /callback: a stuck learner taps Call me, types their number once,
and the Retell outbound agent rings them back in seconds. The request
files a CRM contact off the request path so the ops channel sees it.

Abuse posture: the endpoint places real phone calls, so it is a
toll-fraud surface — honeypot for bots, per-number + per-IP rate
limits, US/CA numbers only (validated in the model).
"""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.orm import Session as DbSession

from backend.api.deps import get_db, get_optional_account
from backend.models.help_request import CallbackRequest, CallbackResponse
from backend.services import retell_calls
from backend.services.rate_limit import RateLimit, check_and_increment

log = logging.getLogger(__name__)

router = APIRouter()

_CALLBACK_LIMIT = RateLimit(
    action="help.callback", max_per_window=3, window_seconds=86400
)


@router.post("/callback", response_model=CallbackResponse)
def request_callback(
    body: CallbackRequest,
    request: Request,
    background: BackgroundTasks,
    db: DbSession = Depends(get_db),
    account=Depends(get_optional_account),
) -> CallbackResponse:
    """Request an immediate callback from the MyNaani assistant.

    Honeypot rejects bots silently with a synthetic "calling" response —
    the surface never reveals which check tripped (same contract as the
    partner-inquiry path).
    """
    if body.website:
        return CallbackResponse(status="calling", calling=True)

    ip = request.client.host if request.client else "unknown"
    for identifier in (body.phone, ip):
        if not check_and_increment(db, _CALLBACK_LIMIT, identifier):
            db.commit()
            return CallbackResponse(status="calling", calling=True)
    db.commit()

    call_id = retell_calls.create_callback(body.phone)
    email = getattr(account, "email", None)
    background.add_task(retell_calls.file_help_contact, body.phone, body.context, email)
    if call_id is None:
        log.warning("help_callback_not_dialed", extra={"phone_tail": body.phone[-4:]})
        return CallbackResponse(status="queued", calling=False)
    return CallbackResponse(status="calling", calling=True)
