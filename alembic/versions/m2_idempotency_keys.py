"""M2: add idempotency_keys table (P14/P15 red item fix)

Revision ID: m2_idempotency_keys
Revises: m1_login_schema
Create Date: 2026-05-28

The idempotency_keys table was defined in backend/models/billing.py
(IdempotencyKey ORM class) but was never created by any migration.
This left the billing checkout endpoint referencing a table that did
not exist, causing 500 errors on idempotency-key reuse.

This migration is purely additive. No existing tables or rows are modified.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "m2_idempotency_keys"
down_revision: Union[str, Sequence[str], None] = "m1_login_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "idempotency_keys",
        sa.Column("key", sa.String(length=128), primary_key=True),
        sa.Column("outcome_json", sa.String(length=4096), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_table("idempotency_keys")
