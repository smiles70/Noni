"""launch schema: accounts, sessions, billing, learning, governance

Revision ID: 0003_launch_schema
Revises: b2c3_telem_rich
Create Date: 2026-05-11

Adds the full launch-readiness schema per docs/architecture/SCHEMA.md and
ADRs 0022-0025. Additive: does not alter existing telemetry_events; new
launch tables are created alongside. Existing dev/CI databases stamped at
b2c3_telem_rich will upgrade cleanly.

Tables created (in dependency order):
  accounts, learners, sessions,
  products, purchases, entitlements, processed_webhook_events,
  units, progress, estimator_state,
  deletion_requests, rate_limit_counters

Plus a small set of columns added to telemetry_events to align with
SCHEMA.md without removing the existing ISCS audit columns (ADR 0024's
two-phase destructive change rule: phase 1 additive only).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_launch_schema"
down_revision: Union[str, Sequence[str], None] = "b2c3_telem_rich"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Required Postgres extensions (idempotent; harmless on managed Postgres).
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")

    # ---------- accounts ----------
    op.create_table(
        "accounts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("auth_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("email", postgresql.CITEXT(), nullable=False),
        sa.Column("display_name", sa.String(length=256), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("auth_user_id", name="uq_accounts_auth_user_id"),
        sa.UniqueConstraint("email", name="uq_accounts_email"),
    )
    op.create_index("ix_accounts_auth_user_id", "accounts", ["auth_user_id"])

    # ---------- learners ----------
    op.create_table(
        "learners",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("display_name", sa.String(length=256), nullable=True),
        sa.Column(
            "relationship",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'self'"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "relationship IN ('self','gift_recipient')",
            name="ck_learners_relationship",
        ),
    )
    op.create_index("ix_learners_account_id", "learners", ["account_id"])

    # ---------- sessions ----------
    op.create_table(
        "sessions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("session_token_hash", sa.String(length=128), nullable=False),
        sa.Column(
            "issued_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revocation_reason", sa.String(length=64), nullable=True),
        sa.Column("last_ip", postgresql.INET(), nullable=True),
        sa.Column("last_user_agent", sa.String(length=512), nullable=True),
        sa.UniqueConstraint("session_token_hash", name="uq_sessions_token_hash"),
    )
    op.create_index(
        "ix_sessions_account_active",
        "sessions",
        ["account_id"],
        postgresql_where=sa.text("revoked_at IS NULL"),
    )
    op.create_index(
        "ix_sessions_expires_active",
        "sessions",
        ["expires_at"],
        postgresql_where=sa.text("revoked_at IS NULL"),
    )

    # ---------- products ----------
    op.create_table(
        "products",
        sa.Column("code", sa.String(length=64), primary_key=True),
        sa.Column("display_name", sa.String(length=256), nullable=False),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.Column(
            "currency",
            sa.String(length=3),
            nullable=False,
            server_default=sa.text("'usd'"),
        ),
        sa.Column("stripe_price_id", sa.String(length=128), nullable=True),
        sa.Column(
            "active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "content_version",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.CheckConstraint("price_cents >= 0", name="ck_products_price_nonneg"),
    )

    # ---------- purchases ----------
    op.create_table(
        "purchases",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "buyer_account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id"),
            nullable=False,
        ),
        sa.Column(
            "beneficiary_account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id"),
            nullable=True,
        ),
        sa.Column("gift_claim_token_hash", sa.String(length=128), nullable=True),
        sa.Column("gift_claimed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "product_code",
            sa.String(length=64),
            sa.ForeignKey("products.code"),
            nullable=False,
        ),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("stripe_payment_intent_id", sa.String(length=128), nullable=True),
        sa.Column("stripe_checkout_session_id", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("refunded_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint(
            "stripe_payment_intent_id",
            name="uq_purchases_stripe_payment_intent",
        ),
        sa.UniqueConstraint(
            "stripe_checkout_session_id",
            name="uq_purchases_stripe_checkout_session",
        ),
        sa.UniqueConstraint(
            "gift_claim_token_hash",
            name="uq_purchases_gift_claim_token_hash",
        ),
        sa.CheckConstraint(
            "status IN ('pending','paid','refunded','failed')",
            name="ck_purchases_status",
        ),
    )
    op.create_index(
        "ix_purchases_buyer_created",
        "purchases",
        ["buyer_account_id", sa.text("created_at DESC")],
    )
    op.create_index(
        "ix_purchases_beneficiary",
        "purchases",
        ["beneficiary_account_id"],
        postgresql_where=sa.text("beneficiary_account_id IS NOT NULL"),
    )

    # ---------- entitlements ----------
    op.create_table(
        "entitlements",
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "product_code",
            sa.String(length=64),
            sa.ForeignKey("products.code"),
            primary_key=True,
        ),
        sa.Column(
            "granted_by_purchase_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("purchases.id"),
            nullable=False,
        ),
        sa.Column("content_version", sa.Integer(), nullable=False),
        sa.Column(
            "granted_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revocation_reason", sa.String(length=64), nullable=True),
    )
    op.create_index(
        "ix_entitlements_account_active",
        "entitlements",
        ["account_id"],
        postgresql_where=sa.text("revoked_at IS NULL"),
    )

    # ---------- processed_webhook_events ----------
    op.create_table(
        "processed_webhook_events",
        sa.Column("event_id", sa.String(length=128), primary_key=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column(
            "processed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("idempotency_outcome", sa.String(length=32), nullable=False),
        sa.CheckConstraint(
            "idempotency_outcome IN ('granted','refunded','noop','error')",
            name="ck_processed_webhook_outcome",
        ),
    )

    # ---------- units ----------
    op.create_table(
        "units",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("module_code", sa.String(length=32), nullable=False),
        sa.Column("unit_index", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column(
            "product_code",
            sa.String(length=64),
            sa.ForeignKey("products.code"),
            nullable=True,
        ),
        sa.Column(
            "content_version",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.Column(
            "published_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_units_module", "units", ["module_code", "unit_index"])

    # ---------- progress ----------
    op.create_table(
        "progress",
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "unit_id",
            sa.String(length=128),
            sa.ForeignKey("units.id"),
            primary_key=True,
        ),
        sa.Column(
            "content_version",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column(
            "first_started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "page_count_seen",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.CheckConstraint(
            "status IN ('started','completed')",
            name="ck_progress_status",
        ),
    )
    op.create_index("ix_progress_account_status", "progress", ["account_id", "status"])

    # ---------- estimator_state ----------
    op.create_table(
        "estimator_state",
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "scope",
            sa.String(length=128),
            primary_key=True,
            server_default=sa.text("'global'"),
        ),
        sa.Column("state_blob", sa.LargeBinary(), nullable=False),
        sa.Column("last_stability", sa.Numeric(6, 4), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # ---------- deletion_requests ----------
    op.create_table(
        "deletion_requests",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id"),
            nullable=False,
        ),
        sa.Column(
            "requested_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            sa.String(length=16),
            nullable=False,
            server_default=sa.text("'requested'"),
        ),
        sa.CheckConstraint(
            "status IN ('requested','cancelled','completed')",
            name="ck_deletion_requests_status",
        ),
    )
    op.create_index(
        "ix_deletion_requests_account", "deletion_requests", ["account_id"]
    )

    # ---------- rate_limit_counters ----------
    op.create_table(
        "rate_limit_counters",
        sa.Column("key", sa.String(length=256), primary_key=True),
        sa.Column("count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "window_start",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_rate_limit_counters_expires", "rate_limit_counters", ["expires_at"]
    )

    # ---------- telemetry_events: additive columns for SCHEMA.md alignment ----------
    # Phase 1 (additive only) per ADR 0024. A later cleanup migration may
    # drop the legacy `time`/`event`/`metadata` columns once all code has
    # switched to the new names.
    op.add_column(
        "telemetry_events",
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "telemetry_events",
        sa.Column("session_id", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "telemetry_events",
        sa.Column("unit_id", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "telemetry_events",
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "telemetry_events",
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_telemetry_events_account_occurred",
        "telemetry_events",
        ["account_id", sa.text("occurred_at DESC")],
    )
    op.create_index(
        "ix_telemetry_events_expires", "telemetry_events", ["expires_at"]
    )


def downgrade() -> None:
    # telemetry_events
    op.drop_index("ix_telemetry_events_expires", table_name="telemetry_events")
    op.drop_index(
        "ix_telemetry_events_account_occurred", table_name="telemetry_events"
    )
    op.drop_column("telemetry_events", "expires_at")
    op.drop_column("telemetry_events", "occurred_at")
    op.drop_column("telemetry_events", "unit_id")
    op.drop_column("telemetry_events", "session_id")
    op.drop_column("telemetry_events", "account_id")

    op.drop_index(
        "ix_rate_limit_counters_expires", table_name="rate_limit_counters"
    )
    op.drop_table("rate_limit_counters")

    op.drop_index("ix_deletion_requests_account", table_name="deletion_requests")
    op.drop_table("deletion_requests")

    op.drop_table("estimator_state")

    op.drop_index("ix_progress_account_status", table_name="progress")
    op.drop_table("progress")

    op.drop_index("ix_units_module", table_name="units")
    op.drop_table("units")

    op.drop_table("processed_webhook_events")

    op.drop_index("ix_entitlements_account_active", table_name="entitlements")
    op.drop_table("entitlements")

    op.drop_index("ix_purchases_beneficiary", table_name="purchases")
    op.drop_index("ix_purchases_buyer_created", table_name="purchases")
    op.drop_table("purchases")

    op.drop_table("products")

    op.drop_index("ix_sessions_expires_active", table_name="sessions")
    op.drop_index("ix_sessions_account_active", table_name="sessions")
    op.drop_table("sessions")

    op.drop_index("ix_learners_account_id", table_name="learners")
    op.drop_table("learners")

    op.drop_index("ix_accounts_auth_user_id", table_name="accounts")
    op.drop_table("accounts")

    # Extensions left in place; harmless and may be needed by other migrations.
