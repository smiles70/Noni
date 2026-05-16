/**
 * ClerkAuthSync — bridges Clerk's hook-based auth state into App.
 *
 * ADR 0024 (Bearer model): Clerk's SDK owns the credential lifecycle.
 * App.tsx only needs to know two things:
 *   1. When Clerk has finished hydrating (so the first whoami carries
 *      a token instead of racing the SDK and resolving signed-out).
 *   2. When the user signs in or out (so the rest of the app
 *      re-renders).
 *
 * This component is mounted only in Clerk mode, inside the
 * <ClerkProvider>, because `useAuth()` requires that context. Mounting
 * it in mock mode would crash. App.tsx gates the mount on
 * VITE_AUTH_PROVIDER === "clerk".
 *
 * Returns null — its only job is firing the callbacks. No DOM.
 *
 * Replaces the previous ClerkAuthBridge, which performed a
 * session-cookie exchange against the backend; that endpoint is gone.
 */
import { useEffect } from "react";
import { useAuth } from "@clerk/clerk-react";

interface Props {
  /** Called when we have a deterministic answer about the current auth
   *  state. Two callsites:
   *    - Clerk reports signed-out  -> caller marks signed-out.
   *    - Clerk reports signed-in AND getToken() returns a real JWT
   *      -> caller may safely call /auth/whoami (interceptor will now
   *      attach Authorization). */
  onAuthChanged: () => void;
  /** Called when Clerk reports signed-in but getToken() is not yet
   *  producing a token. Caller should NOT mark signed-out (that would
   *  cause the infinite SignIn redirect loop); it should keep the
   *  pending state and wait. */
  onPending?: () => void;
}

export default function ClerkAuthSync({ onAuthChanged, onPending }: Props) {
  const { isLoaded, isSignedIn, getToken } = useAuth();

  useEffect(() => {
    if (!isLoaded) return;
    let cancelled = false;

    // Signed-out is deterministic: no need to wait for a token.
    if (!isSignedIn) {
      onAuthChanged();
      return;
    }

    // Signed-in: gate on token availability. getToken() can still
    // return null briefly even after isLoaded + isSignedIn are true
    // (Clerk's internal session bind lags hydration in some flows).
    // If we fire whoami before the token is ready, the request goes
    // out without an Authorization header, the backend returns 401,
    // and App.tsx marks signed-out — triggering the loop. Solution:
    // only signal "auth changed" once we have a non-null token.
    (async () => {
      try {
        const token = await getToken();
        if (cancelled) return;
        if (token) {
          onAuthChanged();
        } else if (onPending) {
          onPending();
        }
      } catch {
        if (!cancelled && onPending) onPending();
      }
    })();

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLoaded, isSignedIn]);

  return null;
}
