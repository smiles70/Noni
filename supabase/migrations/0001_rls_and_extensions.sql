-- Noni — Supabase-managed migration: extensions + RLS policies
--
-- Applied by `supabase db push` during `make deploy-prod`.
-- Harmless to run on plain Postgres (statements use IF NOT EXISTS).
--
-- Authoritative for: RLS policies, scheduled jobs, Postgres extensions.
-- App-level schema (tables, columns) lives in Alembic.

-- Extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;
-- pg_cron is enabled at the Supabase project level; we just reference it.

-- ============================================================
-- Row Level Security: tables containing user data
-- ============================================================
ALTER TABLE IF EXISTS accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS learners ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS purchases ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS entitlements ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS estimator_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS telemetry_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS deletion_requests ENABLE ROW LEVEL SECURITY;

-- Service-role-only tables (no permissive policies)
ALTER TABLE IF EXISTS products ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS units ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS processed_webhook_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS rate_limit_counters ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- Policies: accounts can read their own row
-- ============================================================
DROP POLICY IF EXISTS p_accounts_read_own ON accounts;
CREATE POLICY p_accounts_read_own ON accounts
    FOR SELECT
    USING (auth.uid() = auth_user_id);

DROP POLICY IF EXISTS p_accounts_update_own ON accounts;
CREATE POLICY p_accounts_update_own ON accounts
    FOR UPDATE
    USING (auth.uid() = auth_user_id);

-- ============================================================
-- Policies: child tables are read-own via account_id linkage
-- ============================================================
DROP POLICY IF EXISTS p_learners_read_own ON learners;
CREATE POLICY p_learners_read_own ON learners
    FOR SELECT
    USING (
        account_id IN (
            SELECT id FROM accounts WHERE auth_user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS p_sessions_read_own ON sessions;
CREATE POLICY p_sessions_read_own ON sessions
    FOR SELECT
    USING (
        account_id IN (
            SELECT id FROM accounts WHERE auth_user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS p_purchases_read_own ON purchases;
CREATE POLICY p_purchases_read_own ON purchases
    FOR SELECT
    USING (
        buyer_account_id IN (
            SELECT id FROM accounts WHERE auth_user_id = auth.uid()
        )
        OR
        beneficiary_account_id IN (
            SELECT id FROM accounts WHERE auth_user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS p_entitlements_read_own ON entitlements;
CREATE POLICY p_entitlements_read_own ON entitlements
    FOR SELECT
    USING (
        account_id IN (
            SELECT id FROM accounts WHERE auth_user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS p_progress_read_own ON progress;
CREATE POLICY p_progress_read_own ON progress
    FOR SELECT
    USING (
        account_id IN (
            SELECT id FROM accounts WHERE auth_user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS p_estimator_state_read_own ON estimator_state;
CREATE POLICY p_estimator_state_read_own ON estimator_state
    FOR SELECT
    USING (
        account_id IN (
            SELECT id FROM accounts WHERE auth_user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS p_telemetry_events_read_own ON telemetry_events;
CREATE POLICY p_telemetry_events_read_own ON telemetry_events
    FOR SELECT
    USING (
        account_id IN (
            SELECT id FROM accounts WHERE auth_user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS p_deletion_requests_read_own ON deletion_requests;
CREATE POLICY p_deletion_requests_read_own ON deletion_requests
    FOR SELECT
    USING (
        account_id IN (
            SELECT id FROM accounts WHERE auth_user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS p_deletion_requests_insert_own ON deletion_requests;
CREATE POLICY p_deletion_requests_insert_own ON deletion_requests
    FOR INSERT
    WITH CHECK (
        account_id IN (
            SELECT id FROM accounts WHERE auth_user_id = auth.uid()
        )
    );

-- Note: products and units are world-readable for the SPA's marketing/landing
-- pages. They contain no PII. We choose to keep RLS enabled and add a permissive
-- SELECT for the anon role rather than disabling RLS, to keep policy reasoning uniform.
DROP POLICY IF EXISTS p_products_public_read ON products;
CREATE POLICY p_products_public_read ON products
    FOR SELECT
    USING (true);

DROP POLICY IF EXISTS p_units_public_read ON units;
CREATE POLICY p_units_public_read ON units
    FOR SELECT
    USING (true);
