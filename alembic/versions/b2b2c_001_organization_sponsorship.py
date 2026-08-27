"""b2b2c organization sponsorship

Revision ID: b2b2c_001_org_sponsorship
Revises: 663520a73af6
Create Date: 2026-08-27

Adds organizations, org_licenses, and access_codes tables.
See B2B2C-IMPL-001.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b2b2c_001_org_sponsorship"
down_revision: Union[str, Sequence[str], None] = "663520a73af6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("contact_email", sa.String(256), nullable=False),
        sa.Column("admin_email", sa.String(256), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "org_licenses",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "product_code",
            sa.String(64),
            sa.ForeignKey("products.code"),
            nullable=False,
        ),
        sa.Column(
            "purchase_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("purchases.id"),
            nullable=False,
        ),
        sa.Column("total_seats", sa.Integer(), nullable=False, default=0),
        sa.Column("used_seats", sa.Integer(), nullable=False, default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("purchase_id", name="uq_org_licenses_purchase_id"),
    )
    op.create_table(
        "access_codes",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "license_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("org_licenses.id"),
            nullable=False,
        ),
        sa.Column("code_hash", sa.String(128), nullable=False),
        sa.Column(
            "claimed_by_account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id"),
            nullable=True,
        ),
        sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("code_hash", name="uq_access_codes_code_hash"),
    )


def downgrade() -> None:
    op.drop_table("access_codes")
    op.drop_table("org_licenses")
    op.drop_table("organizations")
