"""Gift redemption routes.

See ADR 0021 and `docs/architecture/SCHEMA.md`.

Endpoints:
- POST /api/gifts/preview     read-only token check; renders redemption page
- POST /api/gifts/claim       binds gift to current account, grants entitlement

Both are rate-limited per ADR 0024 to slow brute-force token guessing.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session as DbSession

from backend.api.deps import get_current_account, get_db
from backend.models.accounts import Account
from backend.services import gifts
from backend.services.rate_limit import (
    LIMIT_GIFT_CLAIM_PER_IP,
    client_ip,
    enforce,
)

router = APIRouter()


class GiftTokenBody(BaseModel):
    token: str


class GiftPreviewResponse(BaseModel):
    valid: bool
    product_code: str | None = None
    purchase_id: str | None = None


class GiftClaimResponse(BaseModel):
    purchase_id: str
    product_code: str
    granted_to_account_id: str


@router.post("/preview", response_model=GiftPreviewResponse)
def gift_preview(
    body: GiftTokenBody,
    request: Request,
    db: DbSession = Depends(get_db),
) -> GiftPreviewResponse:
    enforce(db, LIMIT_GIFT_CLAIM_PER_IP, client_ip(request))
    db.commit()  # persist the rate-limit increment

    purchase = gifts.lookup_for_redemption(db, body.token)
    if purchase is None:
        return GiftPreviewResponse(valid=False)
    return GiftPreviewResponse(
        valid=True,
        product_code=purchase.product_code,
        purchase_id=str(purchase.id),
    )


@router.post("/claim", response_model=GiftClaimResponse)
def gift_claim(
    body: GiftTokenBody,
    request: Request,
    account: Account = Depends(get_current_account),
    db: DbSession = Depends(get_db),
) -> GiftClaimResponse:
    enforce(db, LIMIT_GIFT_CLAIM_PER_IP, client_ip(request))
    try:
        purchase = gifts.claim(db, raw_token=body.token, beneficiary_account=account)
    except gifts.GiftClaimError as e:
        db.rollback()
        # Map to a single conservative envelope; do not leak failure cause.
        _ = str(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"envelope_id": "gift.invalid_or_already_claimed"},
        ) from e
    db.commit()
    return GiftClaimResponse(
        purchase_id=str(purchase.id),
        product_code=purchase.product_code,
        granted_to_account_id=str(account.id),
    )
