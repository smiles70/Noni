/**
 * AuthProvider mock-mode unit tests.
 *
 * Validates the BOOT → SIGNED_OUT → AUTHENTICATING → READY flow
 * without requiring the Clerk SDK or network mocks.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { createElement, useEffect } from "react";
import { createRoot } from "react-dom/client";
import { AuthProvider, useAuth } from "../AuthProvider";
import type { AuthContextValue } from "../AuthProvider";

// Force mock mode so Clerk is never loaded.
vi.mock("../../lib/env", () => ({
  AUTH_PROVIDER: "mock",
  IS_DEV: false,
  API_BASE_URL: "http://localhost:8000",
  CLERK_PUBLISHABLE_KEY: "",
  LOG_LEVEL: "info",
  IS_PROD: false,
}));

function CaptureAuth({ captureRef }: { captureRef: { current: AuthContextValue | null } }) {
  const auth = useAuth();
  useEffect(() => {
    captureRef.current = auth;
  }, [auth, captureRef]);
  return null;
}

describe("AuthProvider — mock mode", () => {
  beforeEach(() => {
    localStorage.clear();
    // Return context-appropriate responses per URL.
    vi.stubGlobal(
      "fetch",
      vi.fn(async (_url: RequestInfo | URL) => {
        const url = _url.toString();
        if (url.includes("/auth/config")) {
          return new Response(
            JSON.stringify({ provider: "mock", version: "0.1.0" }),
            { status: 200, headers: { "content-type": "application/json" } }
          );
        }
        return new Response(
          JSON.stringify({ subject: "sub-1", materialized: true, account_id: "acc-1" }),
          { status: 200, headers: { "content-type": "application/json" } }
        );
      })
    );
  });

  afterEach(() => {
    localStorage.clear();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("boots into SIGNED_OUT when no mock token exists", async () => {
    const captured: { current: AuthContextValue | null } = { current: null };
    const container = document.createElement("div");
    const root = createRoot(container);
    root.render(
      createElement(
        AuthProvider,
        {
          children: createElement(CaptureAuth, { captureRef: captured }),
        }
      )
    );
    await vi.waitFor(() => {
      if (!captured.current) throw new Error("not captured");
      expect(captured.current.state.status).toBe("SIGNED_OUT");
    });
    root.unmount();
  });

  it("signOut transitions to SIGNED_OUT and clears token", async () => {
    localStorage.setItem("noni.mock_token", "mock:test@example.com");
    const captured: { current: AuthContextValue | null } = { current: null };
    const container = document.createElement("div");
    const root = createRoot(container);
    root.render(
      createElement(
        AuthProvider,
        {
          children: createElement(CaptureAuth, { captureRef: captured }),
        }
      )
    );

    await vi.waitFor(() => {
      if (!captured.current) throw new Error("not captured");
      expect(captured.current.state.status).toBe("READY");
    });

    // vi.waitFor succeeded → captured.current is non-null.
    await captured.current!.signOut();
    await vi.waitFor(() => {
      expect(captured.current!.state.status).toBe("SIGNED_OUT");
    });
    expect(localStorage.getItem("noni.mock_token")).toBeNull();
    root.unmount();
  });

  it("exposes retryAuth in context", async () => {
    const captured: { current: AuthContextValue | null } = { current: null };
    const container = document.createElement("div");
    const root = createRoot(container);
    root.render(
      createElement(
        AuthProvider,
        {
          children: createElement(CaptureAuth, { captureRef: captured }),
        }
      )
    );
    await vi.waitFor(() => {
      if (!captured.current) throw new Error("not captured");
      expect(typeof captured.current.retryAuth).toBe("function");
    });
    root.unmount();
  });

  it("transitions to SIGNED_OUT on 401 from /auth/session", async () => {
    const captured: { current: AuthContextValue | null } = { current: null };
    const container = document.createElement("div");
    const root = createRoot(container);

    // Seed a mock token so AuthProvider thinks the user is signed in.
    localStorage.setItem("noni.mock_token", "mock:test@example.com");

    // Mock fetch to return 401 Unauthorized.
    const originalFetch = globalThis.fetch;
    globalThis.fetch = vi.fn(async () =>
      new Response(JSON.stringify({ detail: { error: { code: "auth.no_credential" } } }), {
        status: 401,
        statusText: "Unauthorized",
        headers: { "content-type": "application/json" },
      })
    ) as unknown as typeof fetch;

    root.render(
      createElement(
        AuthProvider,
        {
          children: createElement(CaptureAuth, { captureRef: captured }),
        }
      )
    );

    await vi.waitFor(() => {
      if (!captured.current) throw new Error("not captured");
      expect(captured.current.state.status).toBe("SIGNED_OUT");
    });

    // signOut is invoked on 401 so the credential source stays in sync.
    expect(localStorage.getItem("noni.mock_token")).toBeNull();

    globalThis.fetch = originalFetch;
    root.unmount();
  });
});
