"""Merge epic002 preferences and m2 idempotency keys

Revision ID: 663520a73af6
Revises: epic002_account_preferences, m2_idempotency_keys
Create Date: 2026-08-27 02:17:59.744137

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '663520a73af6'
down_revision: Union[str, Sequence[str], None] = ('epic002_account_preferences', 'm2_idempotency_keys')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
