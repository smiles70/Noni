"""N8N-HELP-001: make support_requests.reply_email nullable.

Revision ID: n8n_help_email_optional
Revises: n8n_help_schema_v2_1
"""

import sqlalchemy as sa
from alembic import op

revision = "n8n_help_email_optional"
down_revision = "n8n_help_schema_v2_1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "support_requests",
        "reply_email",
        existing_type=sa.String(length=256),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "support_requests",
        "reply_email",
        existing_type=sa.String(length=256),
        nullable=False,
    )
