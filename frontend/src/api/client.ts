/**
 * Authenticated API client (ADR 0024 — Bearer model).
 *
 * Post-AuthProvider cutover (2026-05-17) this module hosts:
 *   - The shared `apiClient` axios instance every authenticated call
 *     goes through (B2 single credential pipeline).
 *   - A mock-mode interceptor that reads `mock:<email>` from
 *     localStorage and attaches it as Bearer. Used by both the mock
 *     SignInPage flow and any test client that writes the token key
 *     directly.
 *   - Mock-mode token write/clear helpers (re-exported by `./auth`).
 *
 * The Clerk-mode Bearer is attached by AuthProvider's single
 * apiClient.interceptors.request.use(...) inside the React tree, NOT
 * by this module.
 *
 * Why no `withCredentials`: Bearer tokens are stateless; sending
 * cookies would (a) opt into the credentialed CORS path the backend
 * has explicitly disabled (allow_credentials=False) and (b) re-create
 * the cross-origin cookie footgun we removed in ADR 0024.
 *
 * Why no token-refresh logic here: Clerk's SDK auto-refreshes; mock
 * tokens never expire. If `getToken()` (called inside AuthProvider's
 * interceptor) returns null the user is genuinely signed out, and
 * AuthProvider's state machine handles the transition.
 */
import type { AxiosInstance } from "axios";
import axios from "axios";

interface ImportMetaEnvShape {
  VITE_API_BASE_URL?: string;
  VITE_AUTH_PROVIDER?: string;
}
const _env: ImportMetaEnvShape =
  (import.meta as unknown as { env?: ImportMetaEnvShape }).env ?? {};

export const API_BASE_URL: string = (
  _env.VITE_API_BASE_URL ?? "http://localhost:8000"
).replace(/\/+$/, "");

// Auth provider switch lives in AuthProvider.tsx via useCredentialSource().

// Single source of truth for the mock-mode localStorage key. SignInPage
// (mock branch), AccountSettingsPage's sign-out, and this client must
// agree; defining the constant here prevents drift.
export const MOCK_TOKEN_KEY = "noni.mock_token";

// Diagnostic removed (Sprint 22 I4): previously leaked auth provider
// and API base URL to browser console on every page load.

// Sprint 22 S3: propagate request-id for distributed tracing.
function _generateRequestId(): string {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;
}

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
});

apiClient.interceptors.request.use((config) => {
  if (!config.headers.get("X-Request-ID")) {
    config.headers.set("X-Request-ID", _generateRequestId());
  }
  return config;
});

// Bearer header attachment lives in AuthProvider's single interceptor
// (B2 single credential pipeline). This module is pure transport: it
// owns no auth logic, no interceptors, and no token-reading side
// effects. Mock-mode and Clerk-mode credentials both flow through
// AuthProvider.tsx's apiClient.interceptors.request.use(...) which
// calls auth.getToken() (mock = localStorage, clerk = SDK).

/** Mock-mode helpers. No-ops are not provided — callers gate on
 *  AUTH_PROVIDER themselves; using these in Clerk mode would conflict
 *  with the SDK's credential ownership. */
export function setMockToken(email: string): void {
  localStorage.setItem(MOCK_TOKEN_KEY, `mock:${email}`);
}

export function clearMockToken(): void {
  localStorage.removeItem(MOCK_TOKEN_KEY);
}
