/**
 * ⚠️ AUTH GUARDRAIL
 *
 * DO NOT add network-based auth functions here.
 * Auth state MUST ONLY come from AuthProvider (`src/auth/AuthProvider.tsx`).
 * `/auth/session` is consumed ONLY inside AuthProvider.
 *
 * Violations of this rule reintroduce:
 *   - B1 (single source of truth) breaches — duplicate auth state.
 *   - B5 (discriminated error semantics) drift.
 *   - I-A (auth correctness) regressions including loop classes.
 *
 * This file may host:
 *   - Mock-mode credential helpers (setMockToken / clearMockToken).
 *   - One-shot mutation endpoints with no auth-state side effects
 *     (deleteAccount, cancelDeletion).
 *
 * It must NOT host:
 *   - whoami() or any function that polls "am I signed in?".
 *   - Any auth-state observer or interceptor.
 *
 * History: ADR 0024 migrated to Bearer; FE step-4 cutover (2026-05-17)
 * removed whoami() and routed all auth state through AuthProvider.
 */
import { apiClient } from "./client";

export { setMockToken, clearMockToken, API_BASE_URL } from "./client";

export async function deleteAccount(): Promise<void> {
  await apiClient.post("/me/delete");
}

export async function cancelDeletion(): Promise<void> {
  await apiClient.post("/me/delete/cancel");
}
