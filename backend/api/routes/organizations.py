"""B2B2C organization sponsorship routes.

See B2B2C-IMPL-001. Organizations buy blocks of seats; learners redeem
single-use access codes.
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session as DbSession

from backend.api.deps import get_current_account, get_db, require_staff
from backend.models.accounts import Account
from backend.models.billing import Product, Purchase
from backend.models.governance import OrgAuditLog
from backend.models.organizations import AccessCode, Organization, OrgLicense
from backend.services import entitlements

router = APIRouter()


# ---------- Models ----------


class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)
    contact_email: str = Field(..., min_length=1, max_length=256)
    admin_email: str = Field(..., min_length=1, max_length=256)
    org_type: str = Field(default="nonprofit", pattern="^(nonprofit|for_profit|health_plan)$")
    community_size: Optional[int] = Field(default=None, ge=1)
    tier: str = Field(default="site", max_length=32)
    custom_flag: bool = False
    parent_org_id: Optional[uuid.UUID] = None


class OrganizationResponse(BaseModel):
    id: str
    name: str
    contact_email: str
    admin_email: str
    status: str


class LicenseCreate(BaseModel):
    product_code: str
    total_seats: int = Field(..., ge=1)
    amount_cents: int = Field(..., ge=0)
    expires_at: Optional[datetime] = None
    invoice_ref: str = Field(default="", max_length=128)


class LicenseResponse(BaseModel):
    id: str
    organization_id: str
    product_code: str
    total_seats: int
    used_seats: int


class CodesCreate(BaseModel):
    count: int = Field(..., ge=1, le=1000)


class CodesResponse(BaseModel):
    license_id: str
    codes: list[str]


class RedeemRequest(BaseModel):
    code: str = Field(..., min_length=8)


class RedeemResponse(BaseModel):
    granted: bool
    product_code: str


class UsageResponse(BaseModel):
    license_id: str
    total_seats: int
    used_seats: int
    remaining: int
    codes: list[dict]


# ---------- Helpers ----------


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def _generate_code() -> str:
    """URL-safe, 48-char random token."""
    return secrets.token_urlsafe(36)


# ---------- Staff routes ----------


@router.post("/org/create", response_model=OrganizationResponse, status_code=201)
def create_organization(
    body: OrganizationCreate,
    db: DbSession = Depends(get_db),
    staff: Account = Depends(require_staff),
) -> Organization:
    org = Organization(
        name=body.name,
        contact_email=body.contact_email,
        admin_email=body.admin_email,
        status="active",
        org_type=body.org_type,
        community_size=body.community_size,
        tier=body.tier,
        custom_flag=body.custom_flag,
        parent_org_id=body.parent_org_id,
    )
    db.add(org)
    db.flush()
    db.add(OrgAuditLog(
        organization_id=org.id, actor_account_id=staff.id,
        action="org.create",
        detail=f"name={body.name} type={body.org_type} tier={body.tier}",
    ))
    db.flush()
    return org


@router.post("/org/{org_id}/license", response_model=LicenseResponse, status_code=201)
def create_license(
    org_id: uuid.UUID,
    body: LicenseCreate,
    db: DbSession = Depends(get_db),
    staff: Account = Depends(require_staff),
) -> OrgLicense:
    product = (
        db.query(Product)
        .filter(Product.code == body.product_code, Product.active.is_(True))
        .one_or_none()
    )
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"envelope_id": "billing.product_unavailable"},
        )

    purchase = Purchase(
        id=uuid.uuid4(),
        buyer_account_id=staff.id,
        product_code=body.product_code,
        amount_cents=body.amount_cents,
        currency="usd",
        status="paid",
    )
    db.add(purchase)

    license_ = OrgLicense(
        organization_id=org_id,
        product_code=body.product_code,
        purchase_id=purchase.id,
        total_seats=body.total_seats,
        used_seats=0,
        expires_at=body.expires_at,
    )
    db.add(license_)
    db.flush()
    db.add(OrgAuditLog(
        organization_id=org_id, actor_account_id=staff.id,
        action="license.create",
        detail=f"seats={body.total_seats} amount_cents={body.amount_cents} invoice={body.invoice_ref or 'card'}",
    ))
    db.flush()
    return license_


@router.post("/org/{license_id}/codes", response_model=CodesResponse, status_code=201)
def generate_codes(
    license_id: uuid.UUID,
    body: CodesCreate,
    db: DbSession = Depends(get_db),
    staff: Account = Depends(require_staff),
) -> dict:
    license_ = db.query(OrgLicense).filter(OrgLicense.id == license_id).one_or_none()
    if license_ is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"envelope_id": "org.license_not_found"},
        )

    existing_count = (
        db.query(AccessCode).filter(AccessCode.license_id == license_id).count()
    )
    if existing_count + body.count > license_.total_seats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"envelope_id": "org.not_enough_seats"},
        )

    codes = []
    for _ in range(body.count):
        token = _generate_code()
        code = AccessCode(
            license_id=license_id,
            code_hash=_hash_code(token),
        )
        db.add(code)
        codes.append(token)

    db.flush()
    return {"license_id": str(license_id), "codes": codes}


@router.get("/org/{org_id}/usage", response_model=UsageResponse)
def org_usage(
    org_id: uuid.UUID,
    db: DbSession = Depends(get_db),
    staff: Account = Depends(require_staff),
) -> dict:
    licenses = db.query(OrgLicense).filter(OrgLicense.organization_id == org_id).all()
    if not licenses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"envelope_id": "org.not_found"},
        )

    # For v1, report the first license.
    license_ = licenses[0]
    code_rows = (
        db.query(AccessCode)
        .filter(AccessCode.license_id == license_.id)
        .order_by(AccessCode.created_at)
        .all()
    )
    return {
        "license_id": str(license_.id),
        "total_seats": license_.total_seats,
        "used_seats": license_.used_seats,
        "remaining": license_.total_seats - license_.used_seats,
        "codes": [
            {
                "id": str(c.id),
                "claimed": c.claimed_by_account_id is not None,
                "claimed_at": c.claimed_at.isoformat() if c.claimed_at else None,
            }
            for c in code_rows
        ],
    }


# ---------- Learner route ----------


@router.post("/org/redeem", response_model=RedeemResponse)
def redeem_code(
    body: RedeemRequest,
    db: DbSession = Depends(get_db),
    account: Account = Depends(get_current_account),
) -> dict:
    code_hash = _hash_code(body.code)
    access = (
        db.query(AccessCode).filter(AccessCode.code_hash == code_hash).one_or_none()
    )
    if access is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"envelope_id": "org.code_not_found"},
        )

    if access.claimed_by_account_id is not None:
        if access.claimed_by_account_id == account.id:
            # Idempotent: already claimed by this account.
            return {
                "granted": True,
                "product_code": access.license.product_code,
            }
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"envelope_id": "org.code_already_claimed"},
        )

    license_ = access.license
    if license_.expires_at is not None and license_.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail={"envelope_id": "org.license_expired"},
        )
    if license_.used_seats >= license_.total_seats:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail={"envelope_id": "org.license_full"},
        )

    access.claimed_by_account_id = account.id
    access.claimed_at = datetime.now(timezone.utc)
    license_.used_seats += 1

    entitlements.grant(
        db,
        account_id=account.id,
        product_code=license_.product_code,
        granted_by_purchase_id=license_.purchase_id,
        content_version=license_.product.content_version,
    )

    db.commit()
    return {"granted": True, "product_code": license_.product_code}


# ---------- OB-2: aggregate-only org dashboard (staff) ----------


@router.get("/org/{org_id}/dashboard")
def org_dashboard(
    org_id: uuid.UUID,
    db: DbSession = Depends(get_db),
    staff: Account = Depends(require_staff),
) -> dict:
    """Aggregate-only org view. The privacy boundary IS the feature:
    no per-learner fields are ever returned here."""
    org = db.query(Organization).filter(Organization.id == org_id).one_or_none()
    if org is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"envelope_id": "org.not_found"},
        )
    licenses = db.query(OrgLicense).filter(OrgLicense.organization_id == org_id).all()
    now = datetime.now(timezone.utc)
    lic_rows = []
    for lic in licenses:
        codes = db.query(AccessCode).filter(AccessCode.license_id == lic.id).all()
        lic_rows.append({
            "license_id": str(lic.id),
            "product_code": lic.product_code,
            "total_seats": lic.total_seats,
            "used_seats": lic.used_seats,
            "codes_issued": len(codes),
            "codes_claimed": sum(1 for c in codes if c.claimed_by_account_id),
            "expires_at": lic.expires_at.isoformat() if lic.expires_at else None,
            "expired": bool(lic.expires_at and lic.expires_at < now),
            "expiring_soon": bool(
                lic.expires_at
                and now < lic.expires_at
                and (lic.expires_at - now).days <= 30
            ),
        })
    return {
        "organization": {
            "id": str(org.id),
            "name": org.name,
            "org_type": org.org_type,
            "tier": org.tier,
            "community_size": org.community_size,
            "status": org.status,
            "parent_org_id": str(org.parent_org_id) if org.parent_org_id else None,
        },
        "licenses": lic_rows,
        "children": [
            {"id": str(c.id), "name": c.name, "status": c.status,
             "org_type": c.org_type, "tier": c.tier}
            for c in db.query(Organization)
            .filter(Organization.parent_org_id == org_id)
            .all()
        ],
        "audit": [
            {
                "action": a.action,
                "detail": a.detail,
                "at": a.created_at.isoformat(),
            }
            for a in db.query(OrgAuditLog)
            .filter(OrgAuditLog.organization_id == org_id)
            .order_by(OrgAuditLog.created_at.desc())
            .limit(50)
            .all()
        ],
    }
