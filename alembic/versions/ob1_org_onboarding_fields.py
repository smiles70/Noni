"""OB-1: org onboarding fields + license expiry.

Revision ID: ob1_org_onboarding
Revises: b2b2c_001_org_sponsorship
Create Date: 2026-09-06

Adds B2B onboarding fields to organizations (org_type, community_size,
tier, custom_flag, parent_org_id) and expires_at to org_licenses.
Purely additive — nullable or defaulted columns only; no existing rows
modified.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "ob1_org_onboarding"
down_revision: Union[str, Sequence[str], None] = "b2b2c_001_org_sponsorship"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column("org_type", sa.String(length=16), nullable=False, server_default="nonprofit"),
    )
    op.add_column(
        "organizations",
        sa.Column("community_size", sa.Integer(), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("tier", sa.String(length=32), nullable=False, server_default="site"),
    )
    op.add_column(
        "organizations",
        sa.Column("custom_flag", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column(
        "organizations",
        sa.Column("parent_org_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_organizations_parent",
        "organizations",
        "organizations",
        ["parent_org_id"],
        ["id"],
    )
    op.add_column(
        "org_licenses",
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("org_licenses", "expires_at")
    op.drop_constraint("fk_organizations_parent", "organizations", type_="foreignkey")
    op.drop_column("organizations", "parent_org_id")
    op.drop_column("organizations", "custom_flag")
    op.drop_column("organizations", "tier")
    op.drop_column("organizations", "community_size")
    op.drop_column("organizations", "org_type")
