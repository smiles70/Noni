"""telemetry richness: promote ISCS decision variables to columns

Revision ID: b2c3_telem_rich
Revises: 4a978b4c94cf
Create Date: 2026-05-09

Adds five nullable columns to telemetry_events that capture the
ISCS decision variables for every audited request. See ADR 0009.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b2c3_telem_rich"
down_revision: Union[str, Sequence[str], None] = "4a978b4c94cf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "telemetry_events",
        sa.Column("request_path", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "telemetry_events", sa.Column("stability", sa.Float(), nullable=True)
    )
    op.add_column(
        "telemetry_events",
        sa.Column("selected_state_id", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "telemetry_events",
        sa.Column("decision_reason", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "telemetry_events", sa.Column("max_complexity", sa.Integer(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("telemetry_events", "max_complexity")
    op.drop_column("telemetry_events", "decision_reason")
    op.drop_column("telemetry_events", "selected_state_id")
    op.drop_column("telemetry_events", "stability")
    op.drop_column("telemetry_events", "request_path")
