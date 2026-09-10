"""P1 guest gift checkout: nullable buyer and buyer email.

Revision ID: p1_guest_gift_checkout
Revises: e7_ops_hygiene
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "p1_guest_gift_checkout"
down_revision = "e7_ops_hygiene"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "purchases",
        "buyer_account_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True,
    )
    op.add_column(
        "purchases",
        sa.Column("buyer_email", sa.String(length=256), nullable=True),
    )
    op.create_index(
        "ix_purchases_buyer_email",
        "purchases",
        ["buyer_email"],
        postgresql_where=sa.text("buyer_email IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_purchases_buyer_email", table_name="purchases")
    op.drop_column("purchases", "buyer_email")
    op.alter_column(
        "purchases",
        "buyer_account_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )
