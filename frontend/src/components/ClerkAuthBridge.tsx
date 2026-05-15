/**
 * ClerkAuthBridge — connects Clerk's session to Noni's session cookie.
 *
 * Mounted only when VITE_AUTH_PROVIDER === 'clerk'. Renders nothing.
 *
 * Lifecycle (session 2 — current):
 *   1. Wait for Clerk to finish loading.
 *   2. When isSignedIn flips true, call getToken() and console.log the
 *      resulting JWT. This proves the browser side of the flow works
 *      without yet touching the backend.
 *
 * Lifecycle (session 3 — planned):
 *   - Replace the console.log with `signIn(token)` from `api/auth.ts`,
 *     which POSTs to `/auth/callback` and sets the noni_session cookie.
 *   - Once the cookie is set, call `onSignedIn()` to advance the app
 *     out of the SignInPage.
 *
 * Hooks must be called unconditionally — that's why this component
 * exists at all rather than the logic being inlined behind a runtime
 * `if (provider === 'clerk')` check inside <App />.
 */
import { useEffect } from "react";
import { useAuth } from "@clerk/clerk-react";

export default function ClerkAuthBridge() {
  const { isLoaded, isSignedIn, getToken } = useAuth();

  useEffect(() => {
    if (!isLoaded) return;
    if (!isSignedIn) return;
    let cancelled = false;
    (async () => {
      try {
        const token = await getToken();
        if (cancelled) return;
        // Session 2 milestone: token visible in the browser. Session 3
        // replaces this with: await signIn(token); onSignedIn();
        // eslint-disable-next-line no-console
        console.info(
          "[ClerkAuthBridge] Clerk session token (length=%d):",
          token?.length ?? 0,
          token,
        );
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error("[ClerkAuthBridge] getToken failed:", err);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [isLoaded, isSignedIn, getToken]);

  return null;
}
