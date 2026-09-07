"""ADMIN-OPS E5: staff_role on accounts (RBAC).

Revision ID: e5_staff_rbac
Revises: e6_account_actions
"""

import sqlalchemy as sa
from alembic import op

revision = "e5_staff_rbac"
down_revision = "e6_account_actions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "accounts", sa.Column("staff_role", sa.String(length=16), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("accounts", "staff_role")
