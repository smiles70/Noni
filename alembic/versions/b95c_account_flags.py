"""B2B: account_flags table for internal support signals.

Revision ID: b95c_account_flags
Revises: b95b_progress_confidence
Create Date: 2026-09-06
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "b95c_account_flags"
down_revision: Union[str, Sequence[str], None] = "b95b_progress_confidence"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "account_flags",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("account_id", UUID(as_uuid=True), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("flag", sa.String(length=64), nullable=False),
        sa.Column("detail", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_account_flags_account_id", "account_flags", ["account_id"])


def downgrade() -> None:
    op.drop_index("ix_account_flags_account_id", table_name="account_flags")
    op.drop_table("account_flags")
