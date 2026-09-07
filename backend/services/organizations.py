"""Organization service — single implementation for org operations.

Extracted from backend.api.routes.organizations (AC-2) so the billing
router and the admin router share one implementation. Routes keep the
HTTP boundary (auth, schemas, status codes); all business logic lives
here.

Privacy contract: engagement helpers are aggregate-only with a
k-anonymity floor (MIN_COHORT). No per-learner fields are ever
returned from this module.
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session as DbSession

from backend.models.accounts import Account
from backend.models.billing import Product, Purchase
from backend.models.governance import OrgAuditLog
from backend.models.organizations import (
    AccessCode,
    Organization,
    OrgContact,
    OrgLicense,
)
from backend.services import entitlements

# ---------- Codes ----------


def hash_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def generate_code_token() -> str:
    """URL-safe, 48-char random token."""
    return secrets.token_urlsafe(36)


# ---------- Staff: provisioning ----------


def create_organization(
    db: DbSession,
    staff: Account,
    *,
    name: str,
    contact_email: str,
    admin_email: str,
    org_type: str,
    community_size: Optional[int],
    tier: str,
    custom_flag: bool,
    parent_org_id: Optional[uuid.UUID],
    address_line1: Optional[str] = None,
    address_line2: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    postal_code: Optional[str] = None,
    phone: Optional[str] = None,
    contacts: Optional[list[dict]] = None,
) -> Organization:
    org = Organization(
        name=name,
        contact_email=contact_email,
        admin_email=admin_email,
        status="active",
        org_type=org_type,
        community_size=community_size,
        tier=tier,
        custom_flag=custom_flag,
        parent_org_id=parent_org_id,
        address_line1=address_line1,
        address_line2=address_line2,
        city=city,
        state=state,
        postal_code=postal_code,
        phone=phone,
    )
    db.add(org)
    db.flush()
    # G3: named contacts; exactly one primary enforced here (service
    # layer, portable across sqlite/postgres — no partial index).
    if contacts:
        seen_primary = False
        for c in contacts:
            primary = bool(c.get("is_primary")) and not seen_primary
            seen_primary = seen_primary or primary
            db.add(
                OrgContact(
                    organization_id=org.id,
                    name=c["name"],
                    email=c.get("email"),
                    phone=c.get("phone"),
                    role=c.get("role") or "contact",
                    is_primary=primary,
                )
            )
        db.flush()
    db.add(
        OrgAuditLog(
            organization_id=org.id,
            actor_account_id=staff.id,
            action="org.create",
            detail=f"name={name} type={org_type} tier={tier}",
        )
    )
    db.flush()
    return org


def create_license(
    db: DbSession,
    staff: Account,
    org_id: uuid.UUID,
    *,
    product_code: str,
    total_seats: int,
    amount_cents: int,
    expires_at: Optional[datetime],
    invoice_ref: str,
) -> OrgLicense:
    product = (
        db.query(Product)
        .filter(Product.code == product_code, Product.active.is_(True))
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
        product_code=product_code,
        amount_cents=amount_cents,
        currency="usd",
        status="paid",
    )
    db.add(purchase)

    license_ = OrgLicense(
        organization_id=org_id,
        product_code=product_code,
        purchase_id=purchase.id,
        total_seats=total_seats,
        used_seats=0,
        expires_at=expires_at,
    )
    db.add(license_)
    db.flush()
    db.add(
        OrgAuditLog(
            organization_id=org_id,
            actor_account_id=staff.id,
            action="license.create",
            detail=f"seats={total_seats} amount_cents={amount_cents} invoice={invoice_ref or 'card'}",
        )
    )
    db.flush()
    return license_


def generate_codes(
    db: DbSession,
    license_id: uuid.UUID,
    *,
    count: int,
) -> list[str]:
    license_ = db.query(OrgLicense).filter(OrgLicense.id == license_id).one_or_none()
    if license_ is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"envelope_id": "org.license_not_found"},
        )

    existing_count = (
        db.query(AccessCode).filter(AccessCode.license_id == license_id).count()
    )
    if existing_count + count > license_.total_seats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"envelope_id": "org.not_enough_seats"},
        )

    codes = []
    for _ in range(count):
        token = generate_code_token()
        db.add(AccessCode(license_id=license_id, code_hash=hash_code(token)))
        codes.append(token)

    db.flush()
    return codes


# ---------- Staff: read surfaces ----------


def org_usage(db: DbSession, org_id: uuid.UUID) -> dict:
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


# ---------- Learner: redemption ----------


def redeem_code(db: DbSession, account: Account, code: str) -> dict:
    code_hash = hash_code(code)
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
    if license_.expires_at is not None and license_.expires_at < datetime.now(
        timezone.utc
    ):
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


# ---------- Aggregate-only engagement ----------


MIN_COHORT = 5  # k-anonymity floor: never report engagement below this


def license_engagement(db: DbSession, codes) -> dict:
    """Per-license aggregate, same k-anonymity floor as the org view."""
    from backend.models.learning import Progress

    ids = [c.claimed_by_account_id for c in codes if c.claimed_by_account_id]
    if len(ids) < MIN_COHORT:
        return {"cohort": len(ids), "min_cohort_met": False}
    completed = (
        db.query(Progress)
        .filter(Progress.account_id.in_(ids), Progress.status == "completed")
        .count()
    )
    return {
        "cohort": len(ids),
        "min_cohort_met": True,
        "units_completed": completed,
    }  # k-anonymity floor: never report engagement below this


def org_engagement(db: DbSession, org_id: uuid.UUID) -> dict:
    """Aggregate engagement for the org's claimed seats. Never per-learner:
    counts only, and only when the cohort meets MIN_COHORT."""
    from backend.models.learning import Progress

    account_ids = [
        r[0]
        for r in db.query(AccessCode.claimed_by_account_id)
        .join(OrgLicense, AccessCode.license_id == OrgLicense.id)
        .filter(
            OrgLicense.organization_id == org_id,
            AccessCode.claimed_by_account_id.isnot(None),
        )
        .all()
    ]
    n = len(account_ids)
    base = {"cohort": n, "min_cohort_met": n >= MIN_COHORT}
    if n < MIN_COHORT:
        return base
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    rows = db.query(Progress).filter(Progress.account_id.in_(account_ids)).all()
    completed = sum(1 for r in rows if r.status == "completed")
    active_7d = sum(
        1
        for r in rows
        if r.completed_at
        and r.completed_at >= week_ago
        or r.first_started_at >= week_ago
    )
    deltas = [
        r.confidence_post - r.confidence_pre
        for r in rows
        if r.confidence_pre is not None and r.confidence_post is not None
    ]
    base.update(
        {
            "units_completed": completed,
            "active_last_7d": min(active_7d, n),
            "avg_confidence_delta": (
                round(sum(deltas) / len(deltas), 2)
                if len(deltas) >= MIN_COHORT
                else None
            ),
            "learners_started": len(
                {r.account_id for r in rows if r.status in ("started", "completed")}
            ),
        }
    )
    return base


# ---------- Public + staff slug ----------


def org_public_page(db: DbSession, slug: str) -> dict:
    """Public hosted-partner page data. Deliberately minimal: name only.
    Everything else (licenses, engagement) stays behind require_staff."""
    org = (
        db.query(Organization)
        .filter(Organization.slug == slug, Organization.status == "active")
        .one_or_none()
    )
    if org is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"envelope_id": "org.not_found"},
        )
    return {"name": org.name, "org_type": org.org_type}


def set_org_slug(db: DbSession, org_id: uuid.UUID, slug: str) -> dict:
    """Staff sets the hosted-page slug (/c/<slug>). Lowercase url-safe only;
    unique across orgs. Setting the same slug again is a no-op."""
    org = db.query(Organization).filter(Organization.id == org_id).one_or_none()
    if org is None:
        raise HTTPException(404, detail={"envelope_id": "org.not_found"})
    if org.slug == slug:
        return {"slug": slug, "changed": False}
    clash = (
        db.query(Organization)
        .filter(Organization.slug == slug, Organization.id != org_id)
        .first()
    )
    if clash is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail={"envelope_id": "org.slug_taken"},
        )
    org.slug = slug
    db.commit()
    return {"slug": slug, "changed": True}


def org_dashboard(db: DbSession, org_id: uuid.UUID) -> dict:
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
        lic_rows.append(
            {
                "license_id": str(lic.id),
                "product_code": lic.product_code,
                "total_seats": lic.total_seats,
                "used_seats": lic.used_seats,
                "codes_issued": len(codes),
                "codes_claimed": sum(1 for c in codes if c.claimed_by_account_id),
                "engagement": license_engagement(db, codes),
                "expires_at": lic.expires_at.isoformat() if lic.expires_at else None,
                "expired": bool(lic.expires_at and lic.expires_at < now),
                "expiring_soon": bool(
                    lic.expires_at
                    and now < lic.expires_at
                    and (lic.expires_at - now).days <= 30
                ),
            }
        )
    return {
        "organization": {
            "id": str(org.id),
            "name": org.name,
            "org_type": org.org_type,
            "tier": org.tier,
            "community_size": org.community_size,
            "status": org.status,
            "parent_org_id": str(org.parent_org_id) if org.parent_org_id else None,
            "address_line1": org.address_line1,
            "address_line2": org.address_line2,
            "city": org.city,
            "state": org.state,
            "postal_code": org.postal_code,
            "phone": org.phone,
        },
        "contacts": [
            {
                "id": str(c.id),
                "name": c.name,
                "email": c.email,
                "phone": c.phone,
                "role": c.role,
                "is_primary": c.is_primary,
            }
            for c in db.query(OrgContact)
            .filter(OrgContact.organization_id == org_id)
            .order_by(OrgContact.is_primary.desc(), OrgContact.created_at)
            .all()
        ],
        "licenses": lic_rows,
        "engagement": org_engagement(db, org_id),
        "children": [
            {
                "id": str(c.id),
                "name": c.name,
                "status": c.status,
                "org_type": c.org_type,
                "tier": c.tier,
            }
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


# ---------- Admin console org queries ----------


def org_search(db: DbSession, q: str) -> list[dict]:
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
    out: list[dict] = []
    for o in orgs:
        lic = (
            db.query(OrgLicense)
            .filter(OrgLicense.organization_id == o.id)
            .order_by(OrgLicense.expires_at.desc())
            .first()
        )
        out.append(
            {
                "id": str(o.id),
                "name": o.name,
                "contact_email": o.contact_email,
                "status": o.status,
                "org_type": o.org_type,
                "tier": o.tier,
                "slug": o.slug,
                "seats_total": lic.total_seats if lic else 0,
                "seats_used": lic.used_seats if lic else 0,
            }
        )
    return out


def org_detail(db: DbSession, org_id: uuid.UUID) -> dict:
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
            "address_line1": org.address_line1,
            "address_line2": org.address_line2,
            "city": org.city,
            "state": org.state,
            "postal_code": org.postal_code,
            "phone": org.phone,
        },
        "contacts": [
            {
                "id": str(c.id),
                "name": c.name,
                "email": c.email,
                "phone": c.phone,
                "role": c.role,
                "is_primary": c.is_primary,
            }
            for c in db.query(OrgContact)
            .filter(OrgContact.organization_id == org_id)
            .order_by(OrgContact.is_primary.desc(), OrgContact.created_at)
            .all()
        ],
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
