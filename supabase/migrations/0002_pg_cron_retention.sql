-- Noni — Supabase-managed migration: scheduled retention jobs
--
-- See ADR 0024. Telemetry retention defaults:
--   - Default expires_at is set by the application at insert time.
--   - This sweep removes rows whose expires_at has passed.
--
-- pg_cron is a Supabase-enabled extension; cron jobs live in the cron schema.

-- Idempotent: unschedule prior version of the job if present, then reschedule.
DO $$
BEGIN
    PERFORM cron.unschedule('noni-telemetry-retention')
    WHERE EXISTS (SELECT 1 FROM cron.job WHERE jobname = 'noni-telemetry-retention');
EXCEPTION WHEN OTHERS THEN
    -- pg_cron not available (e.g. running on plain Postgres). No-op.
    NULL;
END $$;

DO $$
BEGIN
    PERFORM cron.schedule(
        'noni-telemetry-retention',
        '15 3 * * *',  -- 03:15 UTC daily
        $cmd$
            DELETE FROM telemetry_events
            WHERE expires_at IS NOT NULL
              AND expires_at < now();
        $cmd$
    );
EXCEPTION WHEN OTHERS THEN
    NULL;
END $$;

-- Same pattern for rate_limit_counters housekeeping.
DO $$
BEGIN
    PERFORM cron.unschedule('noni-rate-limit-sweep')
    WHERE EXISTS (SELECT 1 FROM cron.job WHERE jobname = 'noni-rate-limit-sweep');
EXCEPTION WHEN OTHERS THEN
    NULL;
END $$;

DO $$
BEGIN
    PERFORM cron.schedule(
        'noni-rate-limit-sweep',
        '*/10 * * * *',  -- every 10 minutes
        $cmd$
            DELETE FROM rate_limit_counters
            WHERE expires_at < now();
        $cmd$
    );
EXCEPTION WHEN OTHERS THEN
    NULL;
END $$;

DO $$
BEGIN
    PERFORM cron.unschedule('noni-webhook-event-retention')
    WHERE EXISTS (SELECT 1 FROM cron.job WHERE jobname = 'noni-webhook-event-retention');
EXCEPTION WHEN OTHERS THEN
    NULL;
END $$;

DO $$
BEGIN
    PERFORM cron.schedule(
        'noni-webhook-event-retention',
        '35 3 * * *',
        $cmd$
            DELETE FROM processed_webhook_events
            WHERE processed_at < now() - interval '30 days';
        $cmd$
    );
EXCEPTION WHEN OTHERS THEN
    NULL;
END $$;
