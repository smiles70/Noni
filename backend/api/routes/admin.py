"""Staff admin console — deterministic ops routes, no agent anywhere.

All routes behind require_staff (env ADMIN_ACCOUNT_IDS allowlist).
Every mutation writes an audit row. Learner data is aggregate-only:
no endpoint in this router returns an individual learner's progress
or confidence values — that boundary is structural, not conventional.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, or_
from sqlalchemy.orm import Session as DbSession

from backend.api.deps import get_db, get_optional_account, require_staff
from backend.models.accounts import Account
from backend.models.billing import Purchase
from backend.models.governance import AccountFlag, OrgAuditLog
from backend.models.organizations import AccessCode, Organization, OrgLicense

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
    account: Account | None = Depends(get_optional_account),
) -> WhoAmIResponse:
    """Soft check for the frontend: returns staff=False rather than 403."""
    from backend.core.config import settings

    allowed = {s.strip() for s in settings.ADMIN_ACCOUNT_IDS.split(",") if s.strip()}
    return WhoAmIResponse(staff=account is not None and str(account.id) in allowed)


# ---------- Org ops ----------


@router.get("/orgs", response_model=list[OrgSummary])
def org_search(
    q: str = Query(..., min_length=3),
    db: DbSession = Depends(get_db),
    _: Account = Depends(require_staff),
) -> list[OrgSummary]:
    like = f"%{q.lower()}%"
    orgs = (
        db.query(Organization)
        .filter(
            or_(
                func.lower(Organization.name).like(like),
                func.lower(Organization.contact_email).like(like),
                func.lower(Organization.slug).like(like),
            )
        )
        .order_by(Organization.name)
        .limit(100)
        .all()
    )
    out: list[OrgSummary] = []
    for o in orgs:
        lic = (
            db.query(OrgLicense)
            .filter(OrgLicense.organization_id == o.id)
            .order_by(OrgLicense.expires_at.desc())
            .first()
        )
        out.append(
            OrgSummary(
                id=str(o.id),
                name=o.name,
                contact_email=o.contact_email,
                status=o.status,
                org_type=o.org_type,
                tier=o.tier,
                slug=o.slug,
                seats_total=lic.total_seats if lic else 0,
                seats_used=lic.used_seats if lic else 0,
            )
        )
    return out


@router.get("/orgs/{org_id}")
def org_detail(
    org_id: uuid.UUID,
    db: DbSession = Depends(get_db),
    _: Account = Depends(require_staff),
) -> dict:
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if org is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "org_not_found")
    licenses = db.query(OrgLicense).filter(OrgLicense.organization_id == org_id).all()
    codes_issued = (
        db.query(func.count(AccessCode.id))
        .filter(AccessCode.organization_id == org_id)
        .scalar()
    ) or 0
    audit = (
        db.query(OrgAuditLog)
        .filter(OrgAuditLog.organization_id == org_id)
        .order_by(OrgAuditLog.created_at.desc())
        .limit(50)
        .all()
    )
    return {
        "org": {
            "id": str(org.id),
            "name": org.name,
            "contact_email": org.contact_email,
            "admin_email": org.admin_email,
            "status": org.status,
            "org_type": org.org_type,
            "tier": org.tier,
            "slug": org.slug,
            "community_size": org.community_size,
            "visible_modules": org.visible_modules,
            "parent_org_id": str(org.parent_org_id) if org.parent_org_id else None,
        },
        "licenses": [
            {
                "id": str(lic.id),
                "product_code": lic.product_code,
                "total_seats": lic.total_seats,
                "used_seats": lic.used_seats,
                "expires_at": lic.expires_at.isoformat() if lic.expires_at else None,
            }
            for lic in licenses
        ],
        "codes_issued": codes_issued,
        "audit": [
            {
                "action": a.action,
                "detail": a.detail,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in audit
        ],
    }


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
