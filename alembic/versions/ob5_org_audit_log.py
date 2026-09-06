"""OB-5: org_audit_log table — append-only audit of org/billing mutations.

Revision ID: ob5_org_audit_log
Revises: ob1_org_onboarding
Create Date: 2026-09-06
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "ob5_org_audit_log"
down_revision: Union[str, Sequence[str], None] = "ob1_org_onboarding"


def upgrade() -> None:
    op.create_table(
        "org_audit_log",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "organization_id",
            sa.UUID(),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "actor_account_id", sa.UUID(), sa.ForeignKey("accounts.id"), nullable=True
        ),
        sa.Column("action", sa.String(length=48), nullable=False),
        sa.Column("detail", sa.String(length=512), nullable=False, server_default=""),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_org_audit_log_org", "org_audit_log", ["organization_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_org_audit_log_org", table_name="org_audit_log")
    op.drop_table("org_audit_log")
