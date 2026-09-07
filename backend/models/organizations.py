"""Organization-sponsorship (B2B2C) ORM models.

See B2B2C-IMPL-001. Org licenses allow organizations to pre-pay for
blocks of seats; learners redeem single-use access codes.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(256), nullable=False)
    contact_email = Column(String(256), nullable=False)
    admin_email = Column(String(256), nullable=False)
    status = Column(String(32), nullable=False, default="active")
    # OB-1: B2B onboarding fields (spec 2026-09-06-b2b-onboarding-spec-001).
    org_type = Column(String(16), nullable=False, default="nonprofit")
    community_size = Column(Integer, nullable=True)
    tier = Column(String(32), nullable=False, default="site")
    custom_flag = Column(Boolean, nullable=False, default=False)
    slug = Column(String(64), nullable=True, unique=True)
    visible_modules = Column(JSON, nullable=True)  # NULL = all modules
    parent_org_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True
    )
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    # ADMIN-IA-001 G3: business location + phone (B2B contact data).
    address_line1 = Column(String(128), nullable=True)
    address_line2 = Column(String(128), nullable=True)
    city = Column(String(128), nullable=True)
    state = Column(String(128), nullable=True)
    postal_code = Column(String(128), nullable=True)
    phone = Column(String(128), nullable=True)

    licenses = relationship("OrgLicense", back_populates="organization")
    children = relationship("Organization")
    contacts = relationship(
        "OrgContact", back_populates="organization", cascade="all, delete-orphan"
    )


class OrgLicense(Base):
    __tablename__ = "org_licenses"
    __table_args__ = (
        UniqueConstraint("purchase_id", name="uq_org_licenses_purchase_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    product_code = Column(String(64), ForeignKey("products.code"), nullable=False)
    purchase_id = Column(UUID(as_uuid=True), ForeignKey("purchases.id"), nullable=False)
    total_seats = Column(Integer, nullable=False, default=0)
    used_seats = Column(Integer, nullable=False, default=0)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    organization = relationship("Organization", back_populates="licenses")
    product = relationship("Product")
    purchase = relationship("Purchase")
    access_codes = relationship("AccessCode", back_populates="license")


class AccessCode(Base):
    __tablename__ = "access_codes"
    __table_args__ = (UniqueConstraint("code_hash", name="uq_access_codes_code_hash"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    license_id = Column(
        UUID(as_uuid=True), ForeignKey("org_licenses.id"), nullable=False
    )
    code_hash = Column(String(128), nullable=False)
    claimed_by_account_id = Column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True
    )
    claimed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    license = relationship("OrgLicense", back_populates="access_codes")


class OrgContact(Base):
    """ADMIN-IA-001 G3: multiple named contacts per organization.

    Business contact data (facilities directors, program coordinators) —
    never learner data. One primary contact enforced in the service layer.
    """

    __tablename__ = "org_contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(256), nullable=False)
    email = Column(String(256), nullable=True)
    phone = Column(String(32), nullable=True)
    role = Column(String(64), nullable=False, default="contact")
    is_primary = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    organization = relationship("Organization", back_populates="contacts")
