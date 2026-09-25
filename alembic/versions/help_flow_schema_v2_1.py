"""N8N-HELP-001: make audit legacy columns nullable.

The previous n8n_support_requests migration created `action` and `detail`
with NOT NULL constraints. After the v2 model switch those columns are
no longer written, so they must be nullable to avoid insertion failures.

Revision ID: n8n_help_schema_v2_1
Revises: n8n_help_schema_v2
"""

import sqlalchemy as sa
from alembic import op

revision = "n8n_help_schema_v2_1"
down_revision = "n8n_help_schema_v2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("support_request_audit", "action", nullable=True)
    op.alter_column("support_request_audit", "detail", nullable=True)


def downgrade() -> None:
    op.alter_column("support_request_audit", "action", nullable=False)
    op.alter_column("support_request_audit", "detail", nullable=False)
