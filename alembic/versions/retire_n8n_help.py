"""Retire N8N-HELP-001: drop support request tables.

The help-request widget and its n8n delivery pipeline are being retired
in favor of the Retell website chat widget (ADR 0032, intake 012).
The feature was staging-only and never shipped to production.

Revision ID: retire_n8n_help
Revises: n8n_help_email_optional
"""

import sqlalchemy as sa
from alembic import op

revision = "retire_n8n_help"
down_revision = "n8n_help_email_optional"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("support_request_audit")
    op.drop_table("support_requests")


def downgrade() -> None:
    # Mirrors backend/models/support_request.py at HEAD (post-v2.1
    # schema). Recreates the tables empty — data is not restorable.
    op.create_table(
        "support_requests",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("request_id", sa.String(length=64), nullable=False,
                  unique=True),
        sa.Column("account_id", sa.Uuid(),
                  sa.ForeignKey("accounts.id"), nullable=True),
        sa.Column("context", sa.String(length=32), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("sub_category", sa.String(length=64), nullable=True),
        sa.Column("severity", sa.String(length=8), nullable=True),
        sa.Column("reply_email", sa.String(length=256), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("page_path", sa.String(length=256), nullable=True),
        sa.Column("client_ip", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("n8n_status", sa.String(length=32), nullable=False),
        sa.Column("n8n_retry_count", sa.Integer(), nullable=False),
        sa.Column("n8n_response_code", sa.Integer(), nullable=True),
        sa.Column("n8n_response_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  nullable=False),
    )
    op.create_table(
        "support_request_audit",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("support_request_id", sa.Uuid(),
                  sa.ForeignKey("support_requests.id"), nullable=False,
                  index=True),
        sa.Column("actor", sa.String(length=64), nullable=True),
        sa.Column("old_status", sa.String(length=32), nullable=True),
        sa.Column("new_status", sa.String(length=32), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False),
    )
