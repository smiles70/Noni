"""n8n help request routes.

Public intake: POST /api/v1/help/requests
Staff admin:   GET /api/v1/help/requests
               PATCH /api/v1/help/requests/{request_id}/status
"""

from __future__ import annotations

import json
import logging
from enum import Enum
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session as DbSession

logger = logging.getLogger(__name__)

from backend.api.deps import get_db, require_staff
from backend.core.config import settings
from backend.models.accounts import Account
from backend.models.support_request import SupportRequest, SupportRequestAudit
from backend.services.rate_limit import LIMIT_HELP_REQUESTS_PER_IP, client_ip, enforce
from backend.tasks.help_tasks import deliver_help_request_to_n8n

router = APIRouter()


class HelpContext(str, Enum):
    caregiver = "caregiver"
    facility = "facility"


CAREGIVER_CATEGORIES = {
    "buying_gift",
    "payment_issue",
    "gift_not_received",
    "redeeming_gift",
    "managing_recipient_access",
    "something_else",
}

FACILITY_CATEGORIES = {
    "partnership_inquiry",
    "licensing_and_seats",
    "onboarding_staff",
    "technical_setup",
    "billing_and_invoice",
    "existing_account_issue",
    "something_else",
}

CATEGORY_BY_CONTEXT = {
    HelpContext.caregiver: CAREGIVER_CATEGORIES,
    HelpContext.facility: FACILITY_CATEGORIES,
}

CATEGORY_SEVERITY: dict[str, str] = {
    "buying_gift": "P3",
    "payment_issue": "P1",
    "gift_not_received": "P1",
    "redeeming_gift": "P2",
    "managing_recipient_access": "P2",
    "partnership_inquiry": "P2",
    "licensing_and_seats": "P2",
    "onboarding_staff": "P2",
    "technical_setup": "P1",
    "billing_and_invoice": "P1",
    "existing_account_issue": "P2",
    "something_else": "P3",
}


class HelpRequestCreate(BaseModel):
    context: HelpContext
    category: str = Field(..., max_length=64)
    message: str = Field(..., max_length=2000)
    reply_email: Optional[str] = Field(None, max_length=256)
    request_id: str = Field(..., max_length=64, min_length=8)
    page_path: Optional[str] = Field(None, max_length=256)
    sub_category: Optional[str] = Field(None, max_length=64)


class HelpRequestUpdate(BaseModel):
    status: str = Field(
        ...,
        pattern=r"^(submitted|open|needs_info|resolved|closed)$",
    )
    note: Optional[str] = Field(None, max_length=512)


class HelpRequestResponse(BaseModel):
    id: str
    request_id: str
    context: str
    category: str
    sub_category: Optional[str]
    severity: Optional[str]
    reply_email: Optional[str]
    message: str
    page_path: Optional[str]
    status: str
    n8n_status: str
    n8n_message: Optional[str]
    created_at: str


def _n8n_message(req: SupportRequest) -> Optional[str]:
    if req.n8n_status != "delivered" or not req.n8n_response_text:
        return None
    try:
        data = json.loads(req.n8n_response_text)
        if isinstance(data, dict):
            return data.get("message")
    except (json.JSONDecodeError, AttributeError, TypeError):
        pass
    return req.n8n_response_text[:512]


def _serialize(req: SupportRequest) -> HelpRequestResponse:
    return HelpRequestResponse(
        id=str(req.id),
        request_id=req.request_id,
        context=req.context,
        category=req.category,
        sub_category=req.sub_category,
        severity=req.severity,
        reply_email=req.reply_email,
        message=req.message,
        page_path=req.page_path,
        status=req.status,
        n8n_status=req.n8n_status,
        n8n_message=_n8n_message(req),
        created_at=req.created_at.isoformat() if req.created_at else "",
    )


@router.post("/requests", response_model=HelpRequestResponse, status_code=status.HTTP_201_CREATED)
def create_help_request(
    body: HelpRequestCreate,
    request: Request,
    db: DbSession = Depends(get_db),
) -> HelpRequestResponse:
    if not getattr(settings, "FEATURE_HELP_REQUESTS", True):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"envelope_id": "help.feature_disabled"},
        )

    enforce(
        db,
        LIMIT_HELP_REQUESTS_PER_IP,
        client_ip(request),
        envelope_id="help.ratelimit_exceeded",
    )

    allowed_categories = CATEGORY_BY_CONTEXT.get(body.context)
    if not allowed_categories or body.category not in allowed_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"envelope_id": "help.invalid_category"},
        )

    if body.reply_email and (
        "@" not in body.reply_email or "." not in body.reply_email.split("@")[-1]
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"envelope_id": "help.invalid_email"},
        )

    existing = (
        db.query(SupportRequest)
        .filter(SupportRequest.request_id == body.request_id)
        .one_or_none()
    )
    if existing is not None:
        return _serialize(existing)

    support = SupportRequest(
        request_id=body.request_id,
        context=body.context.value,
        category=body.category,
        sub_category=body.sub_category,
        severity=CATEGORY_SEVERITY.get(body.category),
        reply_email=body.reply_email,
        message=body.message,
        page_path=body.page_path,
        client_ip=client_ip(request),
    )
    db.add(support)
    db.commit()
    db.refresh(support)

    db.add(
        SupportRequestAudit(
            support_request_id=support.id,
            actor="system",
            new_status="submitted",
            note=f"context={support.context} category={support.category}",
        )
    )
    db.commit()

    task = deliver_help_request_to_n8n.delay(str(support.id))
    try:
        # Wait up to 5 seconds for the n8n auto-ack so the widget can show
        # the immediate answer (e.g., "$39.00") without a separate poll.
        task.get(timeout=5, propagate=False)
    except Exception as exc:
        logger.warning("n8n_delivery_wait_failed id=%s: %s", support.id, exc)
    db.refresh(support)

    return _serialize(support)


@router.get("/requests", response_model=List[HelpRequestResponse])
def list_help_requests(
    db: DbSession = Depends(get_db),
    _: Account = Depends(require_staff),
    context: Optional[str] = None,
    status: Optional[str] = None,
    n8n_status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[HelpRequestResponse]:
    q = db.query(SupportRequest)
    if context:
        q = q.filter(SupportRequest.context == context)
    if status:
        q = q.filter(SupportRequest.status == status)
    if n8n_status:
        q = q.filter(SupportRequest.n8n_status == n8n_status)
    q = q.order_by(SupportRequest.created_at.desc()).limit(limit).offset(offset)
    return [_serialize(r) for r in q.all()]


@router.patch("/requests/{request_id}/status", response_model=HelpRequestResponse)
def update_help_request_status(
    request_id: str,
    body: HelpRequestUpdate,
    db: DbSession = Depends(get_db),
    actor: Account = Depends(require_staff),
) -> HelpRequestResponse:
    req = (
        db.query(SupportRequest)
        .filter(SupportRequest.request_id == request_id)
        .one_or_none()
    )
    if req is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"envelope_id": "help.not_found"},
        )

    old_status = req.status
    req.status = body.status
    db.add(
        SupportRequestAudit(
            support_request_id=req.id,
            actor=str(actor.id),
            old_status=old_status,
            new_status=body.status,
            note=body.note or "",
        )
    )
    db.commit()
    db.refresh(req)
    return _serialize(req)
