/**
 * ClerkTokenBridge — installs the Clerk-backed axios request interceptor.
 *
 * Why inline-install (not a global provider with registration):
 *   The previous design had a module-level `_clerkTokenProvider` that
 *   this component registered on mount. That created a timing race: the
 *   very first whoami() could fire from App.tsx (via ClerkAuthSync's
 *   `onAuthChanged`) BEFORE this component's useEffect ran, in which
 *   case the interceptor saw a null provider and sent the request
 *   without an Authorization header — backend returned 401, App marked
 *   the user signed-out, redirected to sign-in, infinite loop.
 *
 *   By installing the interceptor *inside* this component's useEffect,
 *   and only mounting this component under <ClerkProvider>, we know
 *   useAuth().getToken is wired up to Clerk's live state at the moment
 *   the interceptor closure is created. The interceptor calls
 *   `await getToken()` at request time, which always sees the latest
 *   session.
 *
 *   We also dispatch a `noni:clerk-ready` event when isLoaded flips
 *   true AND the interceptor is installed, so App.tsx can gate its
 *   first whoami on this signal rather than racing it.
 *
 * Source: clerk.com/docs/reference/hooks/use-auth (getToken is stable).
 */
import { useEffect } from "react";
import { useAuth } from "@clerk/clerk-react";
import type { InternalAxiosRequestConfig } from "axios";
import { apiClient, attachBearer } from "../api/client";

export const CLERK_READY_EVENT = "noni:clerk-ready";

export function ClerkTokenBridge(): null {
  const { getToken, isLoaded } = useAuth();

  useEffect(() => {
    if (!isLoaded) return;
    // Install the interceptor with a closure over the live getToken.
    const id = apiClient.interceptors.request.use(
      async (config: InternalAxiosRequestConfig) => {
        try {
          const token = await getToken();
          if (token) {
            // eslint-disable-next-line no-console
            if (!(window as unknown as { __noniLoggedToken?: boolean })
              .__noniLoggedToken) {
              console.warn(
                "[noni.client] interceptor attaching token, first 12:",
                token.slice(0, 12),
              );
              (window as unknown as { __noniLoggedToken?: boolean })
                .__noniLoggedToken = true;
            }
            return attachBearer(config, token);
          }
          // eslint-disable-next-line no-console
          console.warn(
            "[noni.client] interceptor ran but getToken() returned null",
          );
        } catch (err) {
          // eslint-disable-next-line no-console
          console.warn("[noni.client] getToken() threw:", err);
        }
        return config;
      },
    );
    // Signal readiness so App.tsx can fire its first whoami safely.
    window.dispatchEvent(new Event(CLERK_READY_EVENT));
    return () => {
      apiClient.interceptors.request.eject(id);
    };
  }, [isLoaded, getToken]);

  return null;
}
