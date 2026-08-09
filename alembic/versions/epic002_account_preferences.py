"""EPIC-002 Phase 2: Add preferences column to accounts table

Revision ID: epic002_account_preferences
Revises: m1_login_schema
Create Date: 2026-08-09

Source: EPIC-002 Login Loop Fix and Account Setup Flow
This migration adds a preferences column to the accounts table to support
user personalization settings (font size, learning pace, etc.).

The preferences column stores JSON data as a string to allow flexible
storage of user preferences without schema changes for new preference types.

Constraints anchored:
  - B12 schema-token compatibility: preferences is NULLable to maintain
    compatibility with existing accounts that haven't completed onboarding
  - B8 / I-D one subject ↔ one row: no identity changes, just adding
    an optional column for user preferences
  - Geragogy compliance: preferences support accessibility features like
    large text size and flexible learning pace

This migration is purely additive; no row content changes. It is
backwards compatible: existing rows will have NULL preferences until
the user completes account setup.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "epic002_account_preferences"
down_revision: Union[str, Sequence[str], None] = "m1_login_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add preferences column as nullable VARCHAR for JSON storage
    op.add_column(
        "accounts",
        sa.Column(
            "preferences",
            sa.String(1024),
            nullable=True,
            comment="User preferences stored as JSON string (EPIC-002 Phase 2)",
        ),
    )


def downgrade() -> None:
    # Remove preferences column
    op.drop_column("accounts", "preferences")