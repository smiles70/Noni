"""n8n help request routes.

Public intake: POST /api/v1/help/requests
Staff admin:   GET /api/v1/help/requests
               PATCH /api/v1/help/requests/{request_id}/status
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session as DbSession

from backend.api.deps import get_db, require_staff
from backend.models.accounts import Account
from backend.models.support_request import SupportRequest, SupportRequestAudit
from backend.services.rate_limit import LIMIT_HELP_REQUESTS_PER_IP, client_ip, enforce
from backend.tasks.help_tasks import deliver_help_request_to_n8n

router = APIRouter()


class HelpContext(str, Enum):
    caregiver = "caregiver"
    facility = "facility"


CAREGIVER_CATEGORIES = {
    "Buying as a gift",
    "Gift delivery question",
    "Payment issue",
    "Other",
}

FACILITY_CATEGORIES = {
    "Partnership question",
    "Pricing",
    "Implementation support",
    "Technical issue",
    "Other",
}

CATEGORY_BY_CONTEXT = {
    HelpContext.caregiver: CAREGIVER_CATEGORIES,
    HelpContext.facility: FACILITY_CATEGORIES,
}


class HelpRequestCreate(BaseModel):
    context: HelpContext
    category: str = Field(..., max_length=64)
    message: str = Field(..., max_length=2000)
    email: Optional[str] = Field(None, max_length=256)
    request_id: str = Field(..., max_length=64, min_length=8)
    page_path: Optional[str] = Field(None, max_length=256)

    class Config:
        use_enum_values = True


class HelpRequestUpdate(BaseModel):
    status: str = Field(..., pattern=r"^(submitted|n8n_delivered|n8n_failed|resolved)$")
    note: Optional[str] = Field(None, max_length=512)

    class Config:
        use_enum_values = True


class HelpRequestResponse(BaseModel):
    id: str
    request_id: str
    context: str
    category: str
    email: Optional[str]
    message: str
    page_path: Optional[str]
    status: str
    created_at: str


def _serialize(req: SupportRequest) -> HelpRequestResponse:
    return HelpRequestResponse(
        id=str(req.id),
        request_id=req.request_id,
        context=req.context,
        category=req.category,
        email=req.email,
        message=req.message,
        page_path=req.page_path,
        status=req.status,
        created_at=req.created_at.isoformat() if req.created_at else "",
    )


@router.post("/requests", response_model=HelpRequestResponse, status_code=status.HTTP_201_CREATED)
def create_help_request(
    body: HelpRequestCreate,
    request: Request,
    db: DbSession = Depends(get_db),
) -> HelpRequestResponse:
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
        email=body.email,
        message=body.message,
        page_path=body.page_path,
        ip_address=client_ip(request),
    )
    db.add(support)
    db.commit()
    db.refresh(support)

    db.add(
        SupportRequestAudit(
            support_request_id=support.id,
            action="submitted",
            detail=f"context={support.context} category={support.category}",
        )
    )
    db.commit()

    deliver_help_request_to_n8n.delay(str(support.id))

    return _serialize(support)


@router.get("/requests", response_model=List[HelpRequestResponse])
def list_help_requests(
    db: DbSession = Depends(get_db),
    _: Account = Depends(require_staff),
    context: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[HelpRequestResponse]:
    q = db.query(SupportRequest)
    if context:
        q = q.filter(SupportRequest.context == context)
    if status:
        q = q.filter(SupportRequest.status == status)
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
            action="status_change",
            actor_id=actor.id,
            detail=f"{old_status} -> {body.status}; note={body.note or ''}",
        )
    )
    db.commit()
    db.refresh(req)
    return _serialize(req)
