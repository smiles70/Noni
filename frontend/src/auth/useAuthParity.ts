/**
 * Auth provider parity probe — extracted from AuthProvider.tsx
 * to respect the 3-useEffect coupling limit (Safe Yellow P17).
 *
 * Calls /auth/config at mount and dispatches REJECTED if the backend
 * provider does not match the frontend's configured provider.
 */
import { useEffect } from "react";
import { apiClient } from "../api/client";
import { AUTH_PROVIDER } from "../lib/env";

interface AuthConfigResponse {
  provider: string;
  version: string;
}

type AuthState =
  | { status: "BOOT" }
  | { status: "SIGNED_OUT" }
  | { status: "AUTHENTICATING" }
  | { status: "READY"; accountId: string | null; email: string | null; displayName: string | null }
  | { status: "TRANSIENT_ERROR" }
  | { status: "REJECTED"; errorCode: string };

export function useAuthParity(
  setState: (state: AuthState) => void,
): void {
  useEffect(() => {
    async function checkProvider() {
      try {
        const res = await apiClient.get<AuthConfigResponse>("/auth/config");
        const backend = res.data.provider;
        const frontend = AUTH_PROVIDER;

        if (backend !== frontend) {
          setState({
            status: "REJECTED",
            errorCode: "fatal.provider_mismatch",
          });
        }
      } catch {
        // Parity probe failure is non-fatal; auth flow will surface
        // the real error via its own retry logic.
      }
    }

    checkProvider();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
}
