"""ADMIN-OPS-HYGIENE: flag resolution columns.

Revision ID: e7_ops_hygiene
Revises: e5_staff_rbac
"""

import sqlalchemy as sa
from alembic import op

revision = "e7_ops_hygiene"
down_revision = "e5_staff_rbac"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "account_flags",
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "account_flags",
        sa.Column(
            "resolved_by",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id"),
            nullable=True,
        ),
    )
    op.add_column(
        "account_flags",
        sa.Column("resolution_note", sa.String(length=512), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("account_flags", "resolution_note")
    op.drop_column("account_flags", "resolved_by")
    op.drop_column("account_flags", "resolved_at")
