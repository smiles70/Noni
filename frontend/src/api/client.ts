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
import { AxiosHeaders } from "axios";
import type { AxiosInstance, InternalAxiosRequestConfig } from "axios";
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

const AUTH_PROVIDER = _env.VITE_AUTH_PROVIDER ?? "mock";

// Single source of truth for the mock-mode localStorage key. SignInPage
// (mock branch), AccountSettingsPage's sign-out, and this client must
// agree; defining the constant here prevents drift.
export const MOCK_TOKEN_KEY = "noni.mock_token";

// Diagnostic: emit exactly one line at module-load time so we can
// confirm in the browser console which provider the bundle was built
// with, without requiring the user to run anything by hand. This is
// cheap, runs once per page load, and is safe to leave in dev. Remove
// once the auth flow is stable.
// eslint-disable-next-line no-console
console.warn(
  "[noni.client] build provider:",
  AUTH_PROVIDER,
  "api:",
  API_BASE_URL,
);

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
});

/** Attach an Authorization header from an arbitrary token resolver.
 *
 * Shared helper so the mock-mode interceptor (installed below at
 * module load) and AuthProvider's clerk-mode interceptor (installed
 * inside the React tree) write the header identically.
 */
export function attachBearer(
  config: InternalAxiosRequestConfig,
  token: string,
): InternalAxiosRequestConfig {
  if (config.headers instanceof AxiosHeaders) {
    config.headers.set("Authorization", `Bearer ${token}`);
  } else {
    config.headers = new AxiosHeaders({
      ...(config.headers as Record<string, string> | undefined),
      Authorization: `Bearer ${token}`,
    });
  }
  return config;
}

// Mock-mode interceptor: installed at module load. In Clerk mode this
// interceptor is a no-op (mock token key never set) and the real
// Bearer is attached by the single interceptor AuthProvider installs
// via useAuth() inside the React tree (B2).
if (AUTH_PROVIDER === "mock") {
  apiClient.interceptors.request.use(
    async (config: InternalAxiosRequestConfig) => {
      try {
        const token = localStorage.getItem(MOCK_TOKEN_KEY);
        if (token) return attachBearer(config, token);
      } catch {
        // no-op
      }
      return config;
    },
  );
}

/** Mock-mode helpers. No-ops are not provided — callers gate on
 *  AUTH_PROVIDER themselves; using these in Clerk mode would conflict
 *  with the SDK's credential ownership. */
export function setMockToken(email: string): void {
  localStorage.setItem(MOCK_TOKEN_KEY, `mock:${email}`);
}

export function clearMockToken(): void {
  localStorage.removeItem(MOCK_TOKEN_KEY);
}
