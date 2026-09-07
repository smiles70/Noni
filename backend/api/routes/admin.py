"""Staff admin console — deterministic ops routes, no agent anywhere.

All routes behind require_staff (env ADMIN_ACCOUNT_IDS allowlist).
Every mutation writes an audit row. Learner data is aggregate-only:
no endpoint in this router returns an individual learner's progress
or confidence values — that boundary is structural, not conventional.
"""

from __future__ import annotations

import uuid

from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy import func, or_
from sqlalchemy.orm import Session as DbSession

from backend.api.deps import get_db, get_optional_account, require_staff
from backend.models.accounts import Account
from backend.models.billing import Purchase
from backend.models.governance import AccountFlag
from backend.services import admin_auth, organizations as org_service
from backend.services.rate_limit import RateLimit

router = APIRouter()


# ---------- Schemas ----------


class WhoAmIResponse(BaseModel):
    staff: bool


class OrgSummary(BaseModel):
    id: str
    name: str
    contact_email: str
    status: str
    org_type: str
    tier: str
    slug: str | None
    seats_total: int
    seats_used: int


class AccountSummary(BaseModel):
    id: str
    email: str | None
    display_name: str | None
    deleted_at: str | None
    purchase_count: int


# ---------- Who am I (frontend gate) ----------


@router.get("/whoami", response_model=WhoAmIResponse)
def whoami(account: Account = Depends(require_staff)) -> WhoAmIResponse:
    return WhoAmIResponse(staff=True)


@router.get("/whoami-check", response_model=WhoAmIResponse)
def whoami_check(
    authorization: Optional[str] = Header(default=None),
    account: Account | None = Depends(get_optional_account),
) -> WhoAmIResponse:
    """Soft check for the frontend: returns staff=False rather than 403.
    Accepts either a staff session token or an allowlisted account."""
    from backend.core.config import settings

    if admin_auth.staff_subject(authorization) is not None:
        return WhoAmIResponse(staff=True)
    allowed = {s.strip() for s in settings.ADMIN_ACCOUNT_IDS.split(",") if s.strip()}
    return WhoAmIResponse(staff=account is not None and str(account.id) in allowed)


# ---------- Org ops ----------


@router.get("/orgs", response_model=list[OrgSummary])
def org_search(
    q: str = Query(..., min_length=3),
    db: DbSession = Depends(get_db),
    _: Account = Depends(require_staff),
) -> list[OrgSummary]:
    return [OrgSummary(**row) for row in org_service.org_search(db, q)]


@router.get("/orgs/{org_id}")
def org_detail(
    org_id: uuid.UUID,
    db: DbSession = Depends(get_db),
    _: Account = Depends(require_staff),
) -> dict:
    return org_service.org_detail(db, org_id)


# ---------- Account support ----------


@router.get("/accounts", response_model=list[AccountSummary])
def account_search(
    q: str = Query(..., min_length=3),
    db: DbSession = Depends(get_db),
    _: Account = Depends(require_staff),
) -> list[AccountSummary]:
    like = f"%{q.lower()}%"
    accounts = (
        db.query(Account)
        .filter(
            or_(
                func.lower(Account.email).like(like),
                func.lower(Account.display_name).like(like),
            )
        )
        .order_by(Account.created_at.desc())
        .limit(100)
        .all()
    )
    return [
        AccountSummary(
            id=str(a.id),
            email=a.email,
            display_name=a.display_name,
            deleted_at=a.deleted_at.isoformat() if a.deleted_at else None,
            purchase_count=db.query(func.count(Purchase.id))
            .filter(Purchase.buyer_account_id == a.id)
            .scalar()
            or 0,
        )
        for a in accounts
    ]


# ---------- Flags (sharing-signal review) ----------


@router.get("/flags")
def list_flags(
    db: DbSession = Depends(get_db),
    _: Account = Depends(require_staff),
) -> dict:
    rows = (
        db.query(AccountFlag).order_by(AccountFlag.created_at.desc()).limit(200).all()
    )
    return {
        "flags": [
            {
                "id": str(f.id),
                "account_id": str(f.account_id),
                "flag": f.flag,
                "detail": f.detail,
                "created_at": f.created_at.isoformat() if f.created_at else None,
            }
            for f in rows
        ]
    }


# ---------- Staff console login (ADMIN-LOGIN-001) ----------


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    staff: bool
    token: str


LIMIT_ADMIN_LOGIN_PER_IP = RateLimit(
    action="admin_login", max_per_window=5, window_seconds=60
)


@router.post("/login", response_model=AdminLoginResponse)
def admin_login(
    body: AdminLoginRequest,
    request: "Request",
    db: DbSession = Depends(get_db),
) -> AdminLoginResponse:
    """Internal staff-console login — username+password, not Magic/Stripe.

    Rate-limited per IP. Password checked against the env-stored SHA-256
    hash (constant-time). On success issues an HMAC staff session token
    and materializes a per-username staff Account so audit rows keep
    per-actor attribution (kim vs steven are distinct actors even though
    they share the password).
    """
    from backend.services import rate_limit

    rate_limit.enforce(
        db,
        LIMIT_ADMIN_LOGIN_PER_IP,
        rate_limit.client_ip(request),
        envelope_id="admin.login_rate_limited",
    )
    if not admin_auth.credentials_ok(body.username, body.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"envelope_id": "admin.invalid_credentials"},
        )
    username = body.username.strip().lower()
    auth_id = admin_auth.staff_auth_user_id(username)
    account = db.query(Account).filter(Account.auth_user_id == auth_id).first()
    if account is None:
        account = Account(
            auth_user_id=auth_id,
            email=f"{username}@staff.mynaani.internal",
            display_name=username,
        )
        db.add(account)
        db.commit()
    token = admin_auth.issue_staff_token(username)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"envelope_id": "admin.session_unavailable"},
        )
    return AdminLoginResponse(staff=True, token=token)
