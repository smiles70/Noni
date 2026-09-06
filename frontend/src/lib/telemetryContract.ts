/**
 * Telemetry event contract (E72-B1).
 *
 * Anchored to the xAPI Video Profile / IEEE 9274.1.1 guidance: emit
 * coarse *milestones* and real state transitions — never continuous
 * motion. Continuous time-updates inflate storage and dedup cost
 * without improving analytic fidelity.
 *
 * Rules enforced here:
 *   1. Known verbs/milestones only — new event names require adding to
 *      ALLOWED_EVENTS (reviewable in one place).
 *   2. Client-side dedup: an identical event+key within DEDUP_WINDOW_MS
 *      is suppressed (StrictMode double-mounts, tab-switch pause
 *      duplicates, accidental double-taps).
 *   3. Fire-and-forget stays caller-side; this module only decides
 *      whether an emission is *allowed*.
 */

/** Event names permitted to reach the backend. */
export const ALLOWED_EVENTS = new Set([
  // onboarding milestones
  "onboarding.welcome_view",
  "onboarding.account_setup_start",
  "onboarding.account_setup_complete",
  "onboarding.first_lesson_start",
  "onboarding.complete",
  "onboarding.getting_started_view",
  "onboarding.getting_started_complete",
  "onboarding.first_action_complete",
  "onboarding.abandonment",
  "onboarding.error",
  // lesson lifecycle (state transitions only)
  "lesson.initialized",
  "lesson.started",
  "lesson.paused",
  "lesson.resumed",
  "lesson.completed",
  "lesson.abandoned",
  // progress milestones — emit each threshold once per registration
  "lesson.progress.25",
  "lesson.progress.50",
  "lesson.progress.75",
  "lesson.progress.100",
  // retrieval + auth probes already in use
  "retrieval_choice.recorded",
  "auth.render_disagreement",
]);

const DEDUP_WINDOW_MS = 30_000;

const seen = new Map<string, number>();

/**
 * Returns true if this emission should proceed. Suppresses exact
 * (event, key) repeats inside the dedup window.
 */
export function shouldEmit(event: string, key = ""): boolean {
  const k = `${event}::${key}`;
  const now = Date.now();
  const last = seen.get(k);
  if (last !== undefined && now - last < DEDUP_WINDOW_MS) return false;
  seen.set(k, now);
  // Bound map growth: drop entries older than the window.
  if (seen.size > 500) {
    for (const [k2, t] of seen) if (now - t > DEDUP_WINDOW_MS) seen.delete(k2);
  }
  return true;
}

/** True if the event name is part of the contract. */
export function isAllowed(event: string): boolean {
  return ALLOWED_EVENTS.has(event);
}
