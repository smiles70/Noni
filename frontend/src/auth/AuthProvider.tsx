/**********************************************************************
 * AuthProvider — single source of auth state for the SPA.
 *
 * Constraints anchored:
 *   B1   single auth-state owner (this component).
 *   B2   single credential pipeline (one apiClient interceptor).
 *   B3   provider parity probe at boot (T4).
 *   B5   discriminated error handling (TRANSIENT vs REJECTED).
 *   B6   single signOut() routine.
 *   T1/T2/T3   timing: never render gated content before token-ready.
 *   T7   one auth resolution per boot.
 *   I-A  signed-in is sticky on transient backend failures.
 *   I-G  no two components hold contradicting auth state.
 *
 * See docs/design/login-redesign-2026-05-17.md §2.1, §3.1.
 * Tag: login-redesign-v1.
 **********************************************************************/

import React, { createContext, useCallback, useContext, useEffect, useState } from "react";

import { apiClient } from "../api/client";
import { useAuthParity } from "./useAuthParity";
import { useAuthSession, type AuthState } from "./useAuthSession";
import { AUTH_PROVIDER } from "../lib/env";
import { magic } from "../lib/magic";
import { MAGIC_TOKEN_KEY, MOCK_TOKEN_KEY } from "../api/client";

const TOKEN_KEY = AUTH_PROVIDER === "magic" ? MAGIC_TOKEN_KEY : MOCK_TOKEN_KEY;

function useCredentialSource() {
  return {
    isLoaded: true,
    isSignedIn: !!localStorage.getItem(TOKEN_KEY),
    getToken: async () => localStorage.getItem(TOKEN_KEY),
    signOut: async () => {
      localStorage.removeItem(TOKEN_KEY);
      if (AUTH_PROVIDER === "magic" && magic) {
        try {
          await magic.user.logout();
        } catch {
          // best-effort; session is already cleared locally
        }
      }
    },
  };
}

export interface AuthContextValue {
  state: AuthState;
  signOut: () => Promise<void>;
  retryAuth: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}

export function notifyAuthChanged(): void {
  window.dispatchEvent(new Event("noni:auth-changed"));
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const auth = useCredentialSource();

  const [state, setState] = useState<AuthState>({ status: "BOOT" });
  const [, forceRefresh] = useState(0);
  const [retryNonce, setRetryNonce] = useState(0);
  const retryAuth = useCallback(() => setRetryNonce((n) => n + 1), []);

  const [sessionStartTime, setSessionStartTime] = useState<number | null>(null);

  useEffect(() => {
    if (state?.status === "READY" && !sessionStartTime) {
      setSessionStartTime(Date.now());
    } else if (state?.status !== "READY" && sessionStartTime) {
      setSessionStartTime(null);
    }
  }, [state?.status, sessionStartTime]);

  useEffect(() => {
    if (!sessionStartTime || state?.status !== "READY") return;

    const checkTimeout = () => {
      const elapsed = Date.now() - sessionStartTime;
      if (elapsed > 30 * 60 * 1000) {
        auth.signOut?.().catch(() => {});
        setState({ status: "SIGNED_OUT" });
        setSessionStartTime(null);
      }
    };

    const timeoutId = setInterval(checkTimeout, 60000);
    return () => clearInterval(timeoutId);
  }, [sessionStartTime, state?.status, auth.signOut, setState]);

  useEffect(() => {
    function handle() {
      forceRefresh((n) => n + 1);
    }
    window.addEventListener("noni:auth-changed", handle);
    return () => window.removeEventListener("noni:auth-changed", handle);
  }, []);

  useEffect(() => {
    const interceptor = apiClient.interceptors.request.use(async (config) => {
      const token = await auth.getToken();

      if (token) {
        config.headers = config.headers || {};
        config.headers.Authorization = `Bearer ${token}`;
      }

      return config;
    });

    return () => {
      apiClient.interceptors.request.eject(interceptor);
    };
  }, [auth]);

  useAuthParity(setState);
  useAuthSession(auth, setState, retryNonce);

  async function signOut() {
    await auth.signOut();
    setState({ status: "SIGNED_OUT" });
    notifyAuthChanged();
  }

  return (
    <AuthContext.Provider value={{ state, signOut, retryAuth }}>
      {children}
    </AuthContext.Provider>
  );
}
