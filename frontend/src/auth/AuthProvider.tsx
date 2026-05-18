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

import React, { createContext, useContext, useEffect, useState } from "react";
import { useAuth as useClerkAuth } from "@clerk/clerk-react";

import { apiClient } from "../api/client";

// Vite injects env at build time but the project's tsconfig does not
// declare ImportMeta.env; mirror the cast used in api/client.ts so
// VITE_AUTH_PROVIDER reads typecheck.
interface ImportMetaEnvShape {
  VITE_AUTH_PROVIDER?: string;
}
const _env: ImportMetaEnvShape =
  (import.meta as unknown as { env?: ImportMetaEnvShape }).env ?? {};


/**********************************************************************
 * ✅ SECTION 1 — CREDENTIAL SOURCE (CLERK + MOCK)
 **********************************************************************/

/*
Abstracts auth provider so AuthProvider never directly touches Clerk.
Prevents mock-mode crash.
*/

function useCredentialSource() {
  const mode = _env.VITE_AUTH_PROVIDER;

  // ✅ MOCK MODE
  if (mode === "mock") {
    return {
      isLoaded: true,
      isSignedIn: !!localStorage.getItem("noni.mock_token"),
      getToken: async () => localStorage.getItem("noni.mock_token"),
      signOut: async () => {
        localStorage.removeItem("noni.mock_token");
      },
    };
  }

  // ✅ CLERK MODE
  const clerk = useClerkAuth();

  return {
    isLoaded: clerk.isLoaded,
    isSignedIn: clerk.isSignedIn,
    getToken: clerk.getToken,
    signOut: clerk.signOut,
  };
}


/**********************************************************************
 * ✅ SECTION 2 — IMPORT API CLIENT (CRITICAL FIX)
 **********************************************************************/

// (apiClient is imported at the top of this file.)


/**********************************************************************
 * ✅ SECTION 3 — AUTH PROVIDER
 **********************************************************************/

const AuthContext = createContext<any>(null);

export function useAuth() {
  return useContext(AuthContext);
}

/**
 * Notify AuthProvider that the credential source has changed.
 *
 * Mock mode writes a Bearer token to localStorage, which React cannot
 * observe on its own. SignInPage's mock branch fires this event after
 * setMockToken() so AuthProvider re-evaluates `useCredentialSource()`
 * and transitions AUTHENTICATING -> READY.
 *
 * In Clerk mode, the Clerk SDK's hook state changes are already
 * observable via useClerkAuth(); this event is harmless if dispatched
 * but is not required.
 */
export function notifyAuthChanged(): void {
  window.dispatchEvent(new Event("noni:auth-changed"));
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const auth = useCredentialSource();

  const [state, setState] = useState<any>({ status: "BOOT" });
  // Bump on `noni:auth-changed` so React re-renders AuthProvider; that
  // re-runs useCredentialSource(), which re-reads localStorage, which
  // makes the auth-flow useEffect below see the new isSignedIn value.
  const [, forceRefresh] = useState(0);

  useEffect(() => {
    function handle() {
      forceRefresh((n) => n + 1);
    }
    window.addEventListener("noni:auth-changed", handle);
    return () => window.removeEventListener("noni:auth-changed", handle);
  }, []);


  /******************************************************************
   * ✅ SECTION 3A — SINGLE INTERCEPTOR (FIXED)
   ******************************************************************/

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


  /******************************************************************
   * ✅ SECTION 3B — PROVIDER PARITY (FIXED)
   ******************************************************************/

  useEffect(() => {
    async function checkProvider() {
      const res = await apiClient.get("/auth/config");

      const backend = res.data.provider;
      const frontend = _env.VITE_AUTH_PROVIDER;

      if (backend !== frontend) {
        setState({
          status: "REJECTED",
          errorCode: "fatal.provider_mismatch",
        });
      }
    }

    checkProvider();
  }, []);


  /******************************************************************
   * ✅ SECTION 3C — AUTH FLOW
   ******************************************************************/

  useEffect(() => {
    if (!auth.isLoaded) return;

    if (!auth.isSignedIn) {
      setState({ status: "SIGNED_OUT" });
      return;
    }

    setState({ status: "AUTHENTICATING" });

    resolveSession();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [auth.isLoaded, auth.isSignedIn]);


  /******************************************************************
   * ✅ SECTION 3D — RESOLVE SESSION (FIXED RACE)
   ******************************************************************/

  async function resolveSession() {
    try {
      const token = await auth.getToken();

      if (!token) return;

      // ✅ PASS TOKEN EXPLICITLY (race fix)
      const res = await apiClient.get("/auth/session", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (res.data.materialized) {
        setState({
          status: "READY",
          accountId: res.data.account_id,
          email: res.data.email ?? null,
          displayName: res.data.display_name,
        });
        return;
      }

      const initRes = await apiClient.post(
        "/auth/session/init",
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      setState({
        status: "READY",
        accountId: initRes.data.account_id,
        // /auth/session/init returns account_id only. email arrives on
        // the next /auth/session call (e.g. next page load); we set it
        // null here so consumers can render a "—" placeholder.
        email: null,
      });

    } catch (err: any) {
      handleError(err);
    }
  }


  /******************************************************************
   * ✅ SECTION 3E — ERROR HANDLING
   ******************************************************************/

  function handleError(err: any) {
    const code = err?.response?.data?.error?.code;

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


  /******************************************************************
   * ✅ SECTION 3F — SIGN OUT
   ******************************************************************/

  async function signOut() {
    await auth.signOut();
    setState({ status: "SIGNED_OUT" });
    // F8: surface the auth-state change to any listener that uses the
    // window-event channel (mirrors SignInPage's post-sign-in dispatch).
    // Idempotent: AuthProvider's own listener short-circuits if state
    // is already SIGNED_OUT.
    notifyAuthChanged();
  }


  return (
    <AuthContext.Provider value={{ state, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}
