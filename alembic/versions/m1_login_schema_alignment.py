"""M1: login-schema alignment — relax accounts.email (B12)

Revision ID: m1_login_schema
Revises: 0003_launch_schema
Create Date: 2026-05-17

Source: docs/design/login-execution-playbook-2026-05-17.md (Section 2).
This is the FIRST application-affecting commit in the login redesign.
No application logic may change until this migration has applied and
been validated (see Section 2 "Validate immediately after running").

Constraints anchored:
  - B12 schema-token compatibility: accounts.email becomes NULLable,
    because the identity provider's default session token may not carry
    email at all. Critical path must not require it.
  - B11 no optional secret on success path: by removing the NOT NULL
    requirement, we sever the synchronous dependency on the optional
    provider Backend API (which previously had to materialize email
    on first sight).
  - B8 / I-D one subject ↔ one row: by dropping the UNIQUE constraint
    on email, we structurally eliminate the email-collision-relink
    failure class (FC3). auth_user_id remains UNIQUE NOT NULL and is
    the only identity key (per `0003_launch_schema`).

This migration is purely structural; no row content changes. It is
backwards compatible: existing rows already carry email values, and
nothing reads the email UNIQUE constraint today.

Rollback is reversible iff no rows with NULL email exist (see
`downgrade()`); see the playbook for the operational gate.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "m1_login_schema"
down_revision: Union[str, Sequence[str], None] = "0003_launch_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the UNIQUE constraint on email FIRST so the column ALTER
    # doesn't fight an index dependency. The constraint name comes from
    # `0003_launch_schema.upgrade()` (sa.UniqueConstraint name).
    op.drop_constraint("uq_accounts_email", "accounts", type_="unique")

    # Make email optional. Identity provider default tokens may not
    # carry an email claim; existing rows are unaffected.
    op.alter_column("accounts", "email", nullable=True)

    # Replace with a NON-UNIQUE partial index for active-row lookup only.
    # This is for read-side performance (e.g., admin email search), not
    # for any uniqueness guarantee.
    op.create_index(
        "idx_accounts_email_active",
        "accounts",
        ["email"],
        unique=False,
        postgresql_where="deleted_at IS NULL",
    )


def downgrade() -> None:
    # SAFETY: the caller is responsible for verifying that no rows have
    # NULL email before invoking this downgrade. The playbook documents
    # this as an operational precondition:
    #     SELECT COUNT(*) FROM accounts WHERE email IS NULL;  -- must be 0
    op.drop_index("idx_accounts_email_active", table_name="accounts")
    op.alter_column("accounts", "email", nullable=False)
    op.create_unique_constraint("uq_accounts_email", "accounts", ["email"])
