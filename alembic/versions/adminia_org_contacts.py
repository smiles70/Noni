"""ADMIN-IA-001 (G3): org location/contact fields + org_contacts table.

Revision ID: adminia_org_contacts
Revises: b95c_account_flags
Create Date: 2026-09-07

Additive only: nullable columns on organizations + a new table with FK
cascade. Zero-downtime; rollback drops the table and columns.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "adminia_org_contacts"
down_revision: Union[str, Sequence[str], None] = "b95c_account_flags"


def upgrade() -> None:
    for col in (
        "address_line1",
        "address_line2",
        "city",
        "state",
        "postal_code",
        "phone",
    ):
        op.add_column("organizations", sa.Column(col, sa.String(128), nullable=True))

    op.create_table(
        "org_contacts",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "organization_id",
            sa.UUID(),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(256), nullable=False),
        # Plain String (not CITEXT) — portable across CI sqlite/postgres.
        sa.Column("email", sa.String(256), nullable=True),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("role", sa.String(64), nullable=False, server_default="contact"),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("org_contacts")
    for col in (
        "phone",
        "postal_code",
        "state",
        "city",
        "address_line2",
        "address_line1",
    ):
        op.drop_column("organizations", col)
