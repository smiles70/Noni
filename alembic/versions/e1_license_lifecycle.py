"""ADMIN-OPS E1: license lifecycle — status, suspension_reason, suspended_at.

Revision ID: e1_license_lifecycle
Revises: adminia_org_contacts
Create Date: 2026-09-07

Additive only: nullable/defaulted columns on org_licenses. Suspend sets
status='suspended'; redeem_code rejects suspended licenses. Zero-downtime;
rollback drops the columns.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e1_license_lifecycle"
down_revision: Union[str, Sequence[str], None] = "adminia_org_contacts"


def upgrade() -> None:
    op.add_column(
        "org_licenses",
        sa.Column(
            "status",
            sa.String(32),
            nullable=False,
            server_default="active",
        ),
    )
    op.add_column(
        "org_licenses",
        sa.Column("suspension_reason", sa.String(256), nullable=True),
    )
    op.add_column(
        "org_licenses",
        sa.Column("suspended_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("org_licenses", "suspended_at")
    op.drop_column("org_licenses", "suspension_reason")
    op.drop_column("org_licenses", "status")
