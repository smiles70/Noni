"""baseline schema

Revision ID: 4a978b4c94cf
Revises:
Create Date: 2026-05-08 09:58:53.128339

Creates the telemetry_events table to match the original create_all() shape.
This file was empty before Sprint 10. Existing dev DBs are already stamped
at this revision so the populated upgrade() is only executed on fresh
databases (e.g. CI Postgres).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "4a978b4c94cf"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "telemetry_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event", sa.String(length=64), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
    )
    op.create_index("ix_telemetry_events_time", "telemetry_events", ["time"])
    op.create_index("ix_telemetry_events_event", "telemetry_events", ["event"])


def downgrade() -> None:
    op.drop_index("ix_telemetry_events_event", table_name="telemetry_events")
    op.drop_index("ix_telemetry_events_time", table_name="telemetry_events")
    op.drop_table("telemetry_events")
