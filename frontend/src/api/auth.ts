/**
 * Auth API surface (ADR 0024 — Bearer model).
 *
 * Post-migration the backend has no /auth/callback and no /auth/signout:
 *   - Sign-in is owned by Clerk's SDK on the client (or by the mock
 *     SignInPage form in dev/tests). The credential is attached to
 *     every request as `Authorization: Bearer <token>` via
 *     `apiClient` from `./client`.
 *   - Sign-out is purely client-side: `clerk.signOut()` drops the
 *     Clerk session, or `clearMockToken()` removes the mock token from
 *     localStorage. Backend tokens we previously issued (none, in this
 *     model) expire on their own.
 *
 * The only authenticated endpoints we still call from this module are
 * /auth/whoami (read) and /me/delete[/cancel] (mutation).
 *
 * Re-exporting `setMockToken`/`clearMockToken` from this module keeps
 * the public auth surface in one place; callers don't need to know
 * about `./client` internals.
 */
import axios from "axios";
import { apiClient } from "./client";

export { setMockToken, clearMockToken, API_BASE_URL } from "./client";

export interface WhoAmIResponse {
  account_id: string;
  // Email may be missing on a deleted-but-not-yet-purged account; the
  // backend returns null in that case rather than 500.
  email: string | null;
  display_name?: string | null;
  has_active_session: boolean;
}

/** Resolve the current account from the attached Bearer.
 *
 * Returns null on 401 (no/invalid token) so callers can branch
 * between "render signed-in" and "render signed-out" without
 * inspecting axios errors. Other errors propagate. */
export async function whoami(): Promise<WhoAmIResponse | null> {
  try {
    const res = await apiClient.get<WhoAmIResponse>("/auth/whoami");
    return res.data;
  } catch (e: unknown) {
    if (axios.isAxiosError(e) && e.response?.status === 401) return null;
    throw e;
  }
}

export async function deleteAccount(): Promise<void> {
  await apiClient.post("/me/delete");
}

export async function cancelDeletion(): Promise<void> {
  await apiClient.post("/me/delete/cancel");
}
