"""N8N-HELP-001: support_requests and support_request_audit tables.

Revision ID: n8n_support_requests
Revises: p1_guest_gift_checkout
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "n8n_support_requests"
down_revision = "p1_guest_gift_checkout"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "support_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("request_id", sa.String(length=64), nullable=False),
        sa.Column("context", sa.String(length=32), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=256), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("page_path", sa.String(length=256), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("n8n_response_code", sa.Integer(), nullable=True),
        sa.Column("n8n_response_text", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("request_id"),
    )
    op.create_index(
        op.f("ix_support_requests_request_id"), "support_requests", ["request_id"], unique=True
    )

    op.create_table(
        "support_request_audit",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "support_request_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("detail", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_support_request_audit_support_request_id"),
        "support_request_audit",
        ["support_request_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_support_request_audit_support_request_id"), table_name="support_request_audit"
    )
    op.drop_table("support_request_audit")
    op.drop_index(op.f("ix_support_requests_request_id"), table_name="support_requests")
    op.drop_table("support_requests")
