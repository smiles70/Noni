"""ADMIN-OPS E6: account suspension columns.

Revision ID: e6_account_actions
Revises: e2_org_lifecycle
"""

import sqlalchemy as sa
from alembic import op

revision = "e6_account_actions"
down_revision = "e2_org_lifecycle"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "accounts",
        sa.Column("suspended_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "accounts",
        sa.Column("suspension_reason", sa.String(length=256), nullable=True),
    )


    op.alter_column("org_audit_log", "organization_id", nullable=True)


def downgrade() -> None:
    op.drop_column("accounts", "suspension_reason")
    op.drop_column("accounts", "suspended_at")
