"""B2B2C organization sponsorship routes.

See B2B2C-IMPL-001. Organizations buy blocks of seats; learners redeem
single-use access codes.

AC-2: business logic lives in backend.services.organizations — this
router is HTTP plumbing only (schemas, auth deps, status codes).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import Path, Body, APIRouter, Depends
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session as DbSession

from backend.api.deps import get_current_account, get_db, require_staff
from backend.models.accounts import Account
from backend.services import organizations as org_service

router = APIRouter()


# ---------- Models ----------


class OrgContactIn(BaseModel):
    """ADMIN-IA-001 G3: named org contact (business contact data)."""

    name: str = Field(..., min_length=1, max_length=256)
    email: Optional[str] = Field(default=None, max_length=256)
    phone: Optional[str] = Field(default=None, max_length=32)
    role: str = Field(default="contact", max_length=64)
    is_primary: bool = False


class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)
    contact_email: str = Field(..., min_length=1, max_length=256)
    admin_email: str = Field(..., min_length=1, max_length=256)
    address_line1: Optional[str] = Field(default=None, max_length=128)
    address_line2: Optional[str] = Field(default=None, max_length=128)
    city: Optional[str] = Field(default=None, max_length=128)
    state: Optional[str] = Field(default=None, max_length=128)
    postal_code: Optional[str] = Field(default=None, max_length=128)
    phone: Optional[str] = Field(default=None, max_length=128)
    contacts: Optional[list[OrgContactIn]] = None
    org_type: str = Field(
        default="nonprofit", pattern="^(nonprofit|for_profit|health_plan)$"
    )
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


# ---------- Staff routes ----------


@router.post("/org/create", response_model=OrganizationResponse, status_code=201)
def create_organization(
    body: OrganizationCreate,
    db: DbSession = Depends(get_db),
    staff: Account = Depends(require_staff),
) -> OrganizationResponse:
    org = org_service.create_organization(
        db,
        staff,
        name=body.name,
        contact_email=body.contact_email,
        admin_email=body.admin_email,
        org_type=body.org_type,
        community_size=body.community_size,
        tier=body.tier,
        custom_flag=body.custom_flag,
        parent_org_id=body.parent_org_id,
        address_line1=body.address_line1,
        address_line2=body.address_line2,
        city=body.city,
        state=body.state,
        postal_code=body.postal_code,
        phone=body.phone,
        contacts=[c.model_dump() for c in body.contacts] if body.contacts else None,
    )
    return OrganizationResponse(
        id=str(org.id),
        name=org.name,
        contact_email=org.contact_email,
        admin_email=org.admin_email,
        status=org.status,
    )


@router.post("/org/{org_id}/license", response_model=LicenseResponse, status_code=201)
def create_license(
    org_id: uuid.UUID,
    body: LicenseCreate,
    db: DbSession = Depends(get_db),
    staff: Account = Depends(require_staff),
) -> LicenseResponse:
    lic = org_service.create_license(
        db,
        staff,
        org_id,
        product_code=body.product_code,
        total_seats=body.total_seats,
        amount_cents=body.amount_cents,
        expires_at=body.expires_at,
        invoice_ref=body.invoice_ref,
    )
    return LicenseResponse(
        id=str(lic.id),
        organization_id=str(lic.organization_id),
        product_code=lic.product_code,
        total_seats=lic.total_seats,
        used_seats=lic.used_seats,
    )


@router.post("/org/{license_id}/codes", response_model=CodesResponse, status_code=201)
def generate_codes(
    license_id: uuid.UUID,
    body: CodesCreate,
    db: DbSession = Depends(get_db),
    staff: Account = Depends(require_staff),
) -> dict:
    codes = org_service.generate_codes(db, license_id, count=body.count)
    return {"license_id": str(license_id), "codes": codes}


@router.get("/org/{org_id}/usage", response_model=UsageResponse)
def org_usage(
    org_id: uuid.UUID,
    db: DbSession = Depends(get_db),
    staff: Account = Depends(require_staff),
) -> dict:
    return org_service.org_usage(db, org_id)


# ---------- Learner route ----------


@router.post("/org/redeem", response_model=RedeemResponse)
def redeem_code(
    body: RedeemRequest,
    db: DbSession = Depends(get_db),
    account: Account = Depends(get_current_account),
) -> dict:
    return org_service.redeem_code(db, account, body.code)


# ---------- Public hosted page ----------


@router.get("/org/by-slug/{slug}")
def org_public_page(
    slug: str = Path(..., max_length=64, pattern=r"^[a-z0-9-]+$"),
    db: DbSession = Depends(get_db),
) -> dict:
    return org_service.org_public_page(db, slug)


@router.post("/org/{org_id}/slug")
def set_org_slug(
    org_id: uuid.UUID,
    slug: str = Body(..., embed=True, max_length=64, pattern=r"^[a-z0-9-]+$"),
    db: DbSession = Depends(get_db),
    staff: Account = Depends(require_staff),
) -> dict:
    return org_service.set_org_slug(db, org_id, slug)


# ---------- OB-2: aggregate-only org dashboard (staff) ----------


@router.get("/org/{org_id}/dashboard")
def org_dashboard(
    org_id: uuid.UUID,
    db: DbSession = Depends(get_db),
    staff: Account = Depends(require_staff),
) -> dict:
    """Aggregate-only org view. The privacy boundary IS the feature:
    no per-learner fields are ever returned here."""
    return org_service.org_dashboard(db, org_id)
