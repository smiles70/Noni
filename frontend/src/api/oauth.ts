/**
 * Supabase-hosted OAuth (Google) — frontend bindings.
 *
 * Why no SDK
 * ----------
 * The supabase-js client is ~30 KB gzipped and pulls in WebSocket / Realtime
 * code we do not use. The OAuth flow is a pair of redirects and a hash
 * fragment parse; we can do that with `window.location` directly and keep
 * the bundle lean.
 *
 * Flow
 * ----
 * 1. User clicks "Continue with Google" on the sign-in page.
 * 2. We redirect to `${SUPABASE_URL}/auth/v1/authorize?provider=google&redirect_to=<APP_URL>`.
 * 3. Supabase handles the Google round-trip and redirects back to APP_URL
 *    with the access token in the URL fragment:
 *      #access_token=<jwt>&refresh_token=<rt>&expires_in=...&token_type=bearer
 * 4. On mount, App.tsx calls `consumeOAuthFragment()`. If it finds a token,
 *    it strips the fragment from the address bar and POSTs the JWT to the
 *    backend `/auth/callback`. The backend's SupabaseAuthProvider verifies
 *    it and mints a session cookie.
 *
 * Configuration
 * -------------
 * Set in `frontend/.env` (Vite reads `VITE_*` at build time):
 *   VITE_AUTH_PROVIDER = "mock" | "supabase"
 *   VITE_SUPABASE_URL  = https://<project-ref>.supabase.co
 *
 * Defaults are "mock" + empty URL, so dev keeps working with no env file.
 */

interface ImportMetaEnvShape {
  VITE_AUTH_PROVIDER?: string;
  VITE_SUPABASE_URL?: string;
}

// Vite injects these at build time. The cast keeps tsc happy without
// pulling in `vite/client` types (we already declare what we need).
const env: ImportMetaEnvShape =
  (import.meta as unknown as { env?: ImportMetaEnvShape }).env ?? {};

export type AuthProviderName = "mock" | "supabase";

export const authProvider: AuthProviderName =
  env.VITE_AUTH_PROVIDER === "supabase" ? "supabase" : "mock";

export const supabaseUrl: string = (env.VITE_SUPABASE_URL ?? "").replace(
  /\/+$/,
  "",
);

/**
 * Redirect the browser to Supabase's OAuth endpoint. The user comes back
 * via the URL fragment; see `consumeOAuthFragment`.
 *
 * Returns `false` (without redirecting) if the provider is not configured
 * — callers can fall back to a friendly error in that case.
 */
export function startGoogleSignIn(): boolean {
  if (authProvider !== "supabase" || !supabaseUrl) return false;
  const returnTo = `${window.location.origin}${window.location.pathname}`;
  const url =
    `${supabaseUrl}/auth/v1/authorize` +
    `?provider=google` +
    `&redirect_to=${encodeURIComponent(returnTo)}`;
  window.location.assign(url);
  return true;
}

export interface OAuthFragment {
  accessToken: string;
  refreshToken?: string;
  expiresIn?: number;
  tokenType?: string;
}

/**
 * Parse `#access_token=...` from a URL hash. Pure function for testability.
 * Returns null when no usable token is present.
 */
export function parseOAuthFragment(hash: string): OAuthFragment | null {
  if (!hash || hash === "#") return null;
  const clean = hash.startsWith("#") ? hash.slice(1) : hash;
  const params = new URLSearchParams(clean);
  const accessToken = params.get("access_token");
  if (!accessToken) return null;
  const expiresInRaw = params.get("expires_in");
  const expiresIn = expiresInRaw ? Number.parseInt(expiresInRaw, 10) : undefined;
  return {
    accessToken,
    refreshToken: params.get("refresh_token") ?? undefined,
    expiresIn: Number.isFinite(expiresIn) ? expiresIn : undefined,
    tokenType: params.get("token_type") ?? undefined,
  };
}

/**
 * If the current URL carries an OAuth fragment, return it and clear the
 * fragment from the address bar so refresh / back-button do not replay it.
 * Returns null if there's nothing to consume.
 */
export function consumeOAuthFragment(): OAuthFragment | null {
  if (typeof window === "undefined") return null;
  const parsed = parseOAuthFragment(window.location.hash);
  if (!parsed) return null;
  // history.replaceState avoids adding a new entry; the user's Back button
  // still goes where they expect.
  window.history.replaceState(
    null,
    "",
    `${window.location.pathname}${window.location.search}`,
  );
  return parsed;
}
