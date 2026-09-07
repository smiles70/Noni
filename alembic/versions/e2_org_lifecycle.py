"""ADMIN-OPS E2: org lifecycle — suspension_reason, suspended_at.

Revision ID: e2_org_lifecycle
Revises: e1_license_lifecycle
Create Date: 2026-09-07

Additive only. Org suspend sets status='suspended'; redemption and code
generation for all its licenses are blocked until reactivated. Children
are NOT cascaded by default (SOC2/Recurly guidance).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e2_org_lifecycle"
down_revision: Union[str, Sequence[str], None] = "e1_license_lifecycle"


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column("suspension_reason", sa.String(256), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("suspended_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("organizations", "suspended_at")
    op.drop_column("organizations", "suspension_reason")
