-- Analytics events table: fire-and-forget product telemetry.
-- Per CONTRACT §IV: no PII, no inference, functional milestones only.
--
-- Event types (hardcoded in backend, not free-form):
--   landing_loaded, dialog_opened, signup_started, signup_completed,
--   curriculum_loaded, lesson_started, lesson_completed,
--   paywall_viewed, checkout_started

CREATE TABLE IF NOT EXISTS analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    session_id UUID NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_analytics_events_event_type
    ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_events_created_at
    ON analytics_events(created_at);
CREATE INDEX IF NOT EXISTS idx_analytics_events_session
    ON analytics_events(session_id);

COMMENT ON TABLE analytics_events IS
    'Contract-compliant event log. No PII. No inference. Fire-and-forget.';
