/**
 * Authenticated API client (ADR 0024 — Bearer model).
 *
 * Every authenticated HTTP call goes through `apiClient` so the Bearer
 * rule lives in exactly one place. Two modes selected at build time by
 * VITE_AUTH_PROVIDER:
 *
 *   clerk: read the current session token from window.Clerk on each
 *          request. Clerk's SDK auto-refreshes the underlying JWT
 *          (~60s lifetime), so a fresh `session.getToken()` returns a
 *          non-expired token whenever the user is signed in. If
 *          window.Clerk is not yet hydrated we send no header; the
 *          ClerkAuthSync component re-runs whoami() once it loads.
 *   mock:  read "mock:<email>" from localStorage. SignInPage's mock
 *          form writes it via `setMockToken`; sign-out (or deletion)
 *          clears it via `clearMockToken`.
 *
 * Why no `withCredentials`: Bearer tokens are stateless; sending
 * cookies would (a) opt into the credentialed CORS path the backend
 * has explicitly disabled (allow_credentials=False) and (b) re-create
 * the cross-origin cookie footgun we just removed.
 *
 * Why no token-refresh logic here: Clerk's SDK handles refresh.
 * If `getToken()` returns null the user is genuinely signed out —
 * trying to refresh ourselves would be guessing.
 */
import axios, { AxiosHeaders } from "axios";
import type { AxiosInstance, InternalAxiosRequestConfig } from "axios";
// Note: `getClerkInstance` exists on @clerk/clerk-expo but NOT on
// @clerk/clerk-react v5. The canonical React pattern for token attach
// inside axios is a small component that uses the `useAuth()` hook to
// register a provider function with this module — see
// ClerkTokenBridge.tsx, which calls `registerClerkTokenProvider` below.

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
 * Shared helper so both the mock-mode interceptor (installed below)
 * and the Clerk-mode interceptor (installed inside ClerkTokenBridge
 * via useAuth) write the header identically.
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
// Bearer is attached by the interceptor that ClerkTokenBridge
// installs via useAuth() inside the React tree.
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
