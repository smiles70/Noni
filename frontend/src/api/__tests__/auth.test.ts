/**
 * Unit tests for `api/auth.ts` (ADR 0024 — Bearer model).
 *
 * Post-migration there is no signIn or signOut to test: those are gone
 * from the API surface. FE step-4 cutover (2026-05-17) further removed
 * whoami() — auth state now flows exclusively from AuthProvider, so
 * the whoami unit test moved with it (deleted, not rehomed: there is
 * no replacement function at this layer by design).
 *
 * What remains here:
 *   - deleteAccount / cancelDeletion path
 *   - mock token helpers write/clear localStorage at the agreed key
 *
 * The axios mock includes `interceptors.request.use` because client.ts
 * registers a Bearer interceptor at module-load time; without it the
 * import itself would crash.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const { mockGet, mockPost, mockUse, isAxiosError } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPost: vi.fn(),
  mockUse: vi.fn(),
  isAxiosError: vi.fn(),
}));

vi.mock("axios", () => ({
  default: {
    create: () => ({
      get: mockGet,
      post: mockPost,
      interceptors: { request: { use: mockUse } },
    }),
    isAxiosError,
  },
  // Named export — client.ts does `import { AxiosHeaders } from "axios"`.
  // The interceptor never runs in unit tests so the value is unused;
  // we just need the import to resolve to something truthy.
  AxiosHeaders: class {},
  isAxiosError,
}));

// Import AFTER vi.mock so the module captures the mocked axios.
import {
  cancelDeletion,
  clearMockToken,
  deleteAccount,
  setMockToken,
} from "../auth";

// Stub localStorage globally for this test file. Vitest's default
// `node` environment doesn't ship one, and adding jsdom for two
// helper tests would be heavier than this 8-line shim.
beforeEach(() => {
  const store: Record<string, string> = {};
  vi.stubGlobal("localStorage", {
    getItem: (k: string) => (k in store ? store[k] : null),
    setItem: (k: string, v: string) => {
      store[k] = v;
    },
    removeItem: (k: string) => {
      delete store[k];
    },
    clear: () => {
      for (const k of Object.keys(store)) delete store[k];
    },
  });
});

afterEach(() => {
  mockGet.mockReset();
  mockPost.mockReset();
  isAxiosError.mockReset();
});

describe("account deletion", () => {
  it("deleteAccount POSTs to /me/delete", async () => {
    mockPost.mockResolvedValueOnce({ data: {} });
    await deleteAccount();
    expect(mockPost).toHaveBeenCalledWith("/me/delete");
  });

  it("cancelDeletion POSTs to /me/delete/cancel", async () => {
    mockPost.mockResolvedValueOnce({ data: {} });
    await cancelDeletion();
    expect(mockPost).toHaveBeenCalledWith("/me/delete/cancel");
  });
});

describe("mock token helpers", () => {
  // These guard the contract between SignInPage (writer), apiClient
  // (reader), and AccountSettingsPage (clearer). The exact key string
  // and value format must stay aligned across all three; if any drifts
  // the bearer interceptor stops finding the token and the user looks
  // perpetually signed-out in mock mode.
  it("setMockToken writes 'mock:<email>' under the agreed key", () => {
    setMockToken("alice@example.test");
    expect(localStorage.getItem("noni.mock_token")).toBe(
      "mock:alice@example.test",
    );
  });

  it("clearMockToken removes the key", () => {
    setMockToken("bob@example.test");
    clearMockToken();
    expect(localStorage.getItem("noni.mock_token")).toBeNull();
  });
});
