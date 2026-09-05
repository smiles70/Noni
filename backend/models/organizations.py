"""Organization-sponsorship (B2B2C) ORM models.

See B2B2C-IMPL-001. Org licenses allow organizations to pre-pay for
blocks of seats; learners redeem single-use access codes.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
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
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    licenses = relationship("OrgLicense", back_populates="organization")


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
