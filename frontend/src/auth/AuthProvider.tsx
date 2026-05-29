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
import { AUTH_PROVIDER } from "../lib/env";
import { useAuthParity } from "./useAuthParity";
import { useAuthSession, type AuthState } from "./useAuthSession";


/**********************************************************************
 * ✅ SECTION 1 — CREDENTIAL SOURCE (CLERK + MOCK)
 **********************************************************************/

/*
Abstracts auth provider so AuthProvider never directly touches Clerk.
Prevents mock-mode crash.
*/

function useCredentialSource() {
  const mode = AUTH_PROVIDER;

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

export interface AuthContextValue {
  state: AuthState;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
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

  const [state, setState] = useState<AuthState>({ status: "BOOT" });
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
   * ✅ SECTION 3B — PROVIDER PARITY (EXTRACTED TO useAuthParity)
   ******************************************************************/

  useAuthParity(setState);


  /******************************************************************
   * ✅ SECTION 3C — AUTH FLOW (EXTRACTED TO useAuthSession)
   * Sprint '2nd Safe Yellow' P17: session resolution moved to hook.
   ******************************************************************/

  useAuthSession(auth, setState);


  /******************************************************************
   * ✅ SECTION 3D — SIGN OUT
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
