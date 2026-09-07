"""B2B path-95: confidence self-report columns on progress.

Revision ID: b95b_progress_confidence
Revises: b95_org_curation_slug
Create Date: 2026-09-06

Additive nullable ints only.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b95b_progress_confidence"
down_revision: Union[str, Sequence[str], None] = "b95_org_curation_slug"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("progress", sa.Column("confidence_pre", sa.Integer(), nullable=True))
    op.add_column("progress", sa.Column("confidence_post", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("progress", "confidence_post")
    op.drop_column("progress", "confidence_pre")
