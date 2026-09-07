"""B2B path-95: partner curation flag + hosted-page slug.

Revision ID: b95_org_curation_slug
Revises: ob5_org_audit_log
Create Date: 2026-09-06

Adds organizations.slug (hosted partner page) and organizations.visible_modules
(JSON list; NULL = all modules — partner curation flag). Additive only.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b95_org_curation_slug"
down_revision: Union[str, Sequence[str], None] = "ob5_org_audit_log"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("organizations", sa.Column("slug", sa.String(length=64), nullable=True))
    op.add_column("organizations", sa.Column("visible_modules", sa.JSON(), nullable=True))
    op.create_unique_constraint("uq_organizations_slug", "organizations", ["slug"])


def downgrade() -> None:
    op.drop_constraint("uq_organizations_slug", "organizations")
    op.drop_column("organizations", "visible_modules")
    op.drop_column("organizations", "slug")
