/**
 * Stage 0 telemetry — frontend probes.
 *
 * Source: docs/design/login-execution-playbook-2026-05-17.md (Section 1B).
 *
 * Constraints anchored:
 *   - I-G  no two components may render contradictory `signedIn` state.
 *          The probe `recordAuthDisagreement()` fires from inside the
 *          (future) <AuthProvider> when an invariant violation is
 *          observed at render time.
 *   - E10  signals must exist before redesign can be measured.
 *
 * This module is a Stage 0 stub. It MUST exist before <AuthProvider> is
 * built (Stage 2) so call sites can be wired during implementation. The
 * current transport is `console.warn`; a real analytics/metrics
 * transport will replace the body without changing the public API.
 */

import { logger } from "../lib/logger";

export interface AuthDisagreementContext {
  /** Logical area that observed the disagreement, e.g. "navbar", "body". */
  readonly site: string;
  /** What the observer believed the auth state to be. */
  readonly observed: string;
  /** What the authoritative AuthContext currently reports. */
  readonly authoritative: string;
}

/**
 * Record a single FE/BE or component-to-context auth-state disagreement
 * (I-G violation probe).
 *
 * Do NOT include tokens, headers, or PII in the context (B10).
 */
export function recordAuthDisagreement(ctx: AuthDisagreementContext): void {
  logger.warn("[METRIC] signedin_render_disagreement", {
    site: ctx.site,
    observed: ctx.observed,
    authoritative: ctx.authoritative,
  });
}
