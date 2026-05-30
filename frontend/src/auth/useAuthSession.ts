/**
 * Auth session resolution — extracted from AuthProvider.tsx
 * (Sprint '2nd Safe Yellow' P17: reduces component line count).
 *
 * Encapsulates the /auth/session + /auth/session/init flow and
 * discriminated error handling.
 */
import { useEffect } from "react";
import { apiClient } from "../api/client";

export type AuthState =
  | { status: "BOOT" }
  | { status: "SIGNED_OUT" }
  | { status: "AUTHENTICATING" }
  | {
      status: "READY";
      accountId: string | null;
      email: string | null;
      displayName: string | null;
    }
  | { status: "TRANSIENT_ERROR" }
  | { status: "REJECTED"; errorCode: string };

interface AuthSessionResponse {
  subject: string;
  materialized: boolean;
  account_id?: string | null;
  email?: string | null;
  display_name?: string | null;
}

interface AuthSessionInitResponse {
  account_id: string;
}

interface ApiErrorResponse {
  data?: { error?: { code?: string } };
}

export function useAuthSession(
  auth: {
    isLoaded: boolean;
    isSignedIn: boolean | undefined;
    getToken: () => Promise<string | null>;
  },
  setState: React.Dispatch<React.SetStateAction<AuthState>>,
  retryNonce?: number,
) {
  useEffect(() => {
    if (!auth.isLoaded) return;

    if (!auth.isSignedIn) {
      setState({ status: "SIGNED_OUT" });
      return;
    }

    setState({ status: "AUTHENTICATING" });

    resolveSession();

    async function resolveSession() {
      try {
        const token = await auth.getToken();
        if (!token) return;

        const res = await apiClient.get<AuthSessionResponse>("/auth/session", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (res.data.materialized) {
          setState({
            status: "READY",
            accountId: res.data.account_id ?? null,
            email: res.data.email ?? null,
            displayName: res.data.display_name ?? null,
          });
          return;
        }

        const initRes = await apiClient.post<AuthSessionInitResponse>(
          "/auth/session/init",
          {},
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        setState({
          status: "READY",
          accountId: initRes.data.account_id,
          email: null,
          displayName: null,
        });
      } catch (err) {
        handleError(err);
      }
    }

    function handleError(err: unknown) {
      const apiErr = err as { response?: ApiErrorResponse } | undefined;
      const code = apiErr?.response?.data?.error?.code;

      if (!code) {
        setState({ status: "TRANSIENT_ERROR" });
        return;
      }

      if (code.startsWith("auth.transient")) {
        setState({ status: "TRANSIENT_ERROR" });
        return;
      }

      setState({
        status: "REJECTED",
        errorCode: code,
      });
    }
  }, [auth.isLoaded, auth.isSignedIn, retryNonce]);
}
