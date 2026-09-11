"""N8N-HELP-001 v2: reconcile support_requests and support_request_audit
with the FRD/PRD schema.

Revision ID: n8n_help_schema_v2
Revises: n8n_support_requests
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "n8n_help_schema_v2"
down_revision = "n8n_support_requests"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # support_requests column renames / additions
    op.add_column(
        "support_requests",
        sa.Column("reply_email", sa.String(length=256), nullable=True),
    )
    op.execute("UPDATE support_requests SET reply_email = COALESCE(email, '')")
    op.alter_column("support_requests", "reply_email", nullable=False)
    op.drop_column("support_requests", "email")

    op.add_column(
        "support_requests",
        sa.Column("client_ip", sa.String(length=64), nullable=True),
    )
    op.execute("UPDATE support_requests SET client_ip = ip_address")
    op.drop_column("support_requests", "ip_address")

    op.add_column(
        "support_requests",
        sa.Column("n8n_status", sa.String(length=32), nullable=False, server_default="pending"),
    )
    op.add_column(
        "support_requests",
        sa.Column("n8n_retry_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "support_requests",
        sa.Column("sub_category", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "support_requests",
        sa.Column("severity", sa.String(length=8), nullable=True),
    )
    op.add_column(
        "support_requests",
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_support_requests_account_id_accounts"),
        "support_requests",
        "accounts",
        ["account_id"],
        ["id"],
    )

    # support_request_audit FRD columns
    op.add_column(
        "support_request_audit",
        sa.Column("actor", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "support_request_audit",
        sa.Column("old_status", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "support_request_audit",
        sa.Column("new_status", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "support_request_audit",
        sa.Column("note", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("support_request_audit", "note")
    op.drop_column("support_request_audit", "new_status")
    op.drop_column("support_request_audit", "old_status")
    op.drop_column("support_request_audit", "actor")

    op.drop_constraint(
        op.f("fk_support_requests_account_id_accounts"), "support_requests", type_="foreignkey"
    )
    op.drop_column("support_requests", "account_id")
    op.drop_column("support_requests", "severity")
    op.drop_column("support_requests", "sub_category")
    op.drop_column("support_requests", "n8n_retry_count")
    op.drop_column("support_requests", "n8n_status")
    op.drop_column("support_requests", "client_ip")
    op.add_column(
        "support_requests",
        sa.Column("ip_address", sa.String(length=64), nullable=True),
    )
    op.drop_column("support_requests", "reply_email")
    op.add_column(
        "support_requests",
        sa.Column("email", sa.String(length=256), nullable=True),
    )
