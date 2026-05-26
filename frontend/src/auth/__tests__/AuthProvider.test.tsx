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
vi.mock("../../lib/env", () => ({ AUTH_PROVIDER: "mock", IS_DEV: false }));

function CaptureAuth({ ref }: { ref: { current: AuthContextValue | null } }) {
  const auth = useAuth();
  useEffect(() => {
    ref.current = auth;
  }, [auth, ref]);
  return null;
}

describe("AuthProvider — mock mode", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it("boots into SIGNED_OUT when no mock token exists", () => {
    const captured: { current: AuthContextValue | null } = { current: null };
    const container = document.createElement("div");
    const root = createRoot(container);
    root.render(
      createElement(
        AuthProvider,
        {
          children: createElement(CaptureAuth, { ref: captured }),
        }
      )
    );
    if (!captured.current) throw new Error("captured was null");
    expect(captured.current.state.status).toBe("SIGNED_OUT");
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
          children: createElement(CaptureAuth, { ref: captured }),
        }
      )
    );

    await vi.waitFor(() => {
      if (!captured.current) throw new Error("not captured");
      expect(captured.current.state.status).toBe("READY");
    });

    // vi.waitFor succeeded → captured.current is non-null.
    await captured.current!.signOut();
    expect(captured.current!.state.status).toBe("SIGNED_OUT");
    expect(localStorage.getItem("noni.mock_token")).toBeNull();
    root.unmount();
  });
});
