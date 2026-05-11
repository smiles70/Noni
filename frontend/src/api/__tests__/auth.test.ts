/**
 * Unit tests for `api/auth.ts`.
 *
 * The auth client is thin (axios + cookies), but its 401-on-whoami swallow
 * behaviour is load-bearing for `NavBar` (which renders the signed-out
 * state on null) and must not regress.
 *
 * We replace the module's exported axios `client` instance methods via
 * vi.mock at module-import time.
 */
import { afterEach, describe, expect, it, vi } from "vitest";

// `vi.mock` is hoisted to the top of the file, above any `const` lines.
// `vi.hoisted` lets us declare the spy fns alongside the mock so they
// initialize together and are accessible inside the factory.
const { mockGet, mockPost, isAxiosError } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPost: vi.fn(),
  isAxiosError: vi.fn(),
}));

vi.mock("axios", () => ({
  default: {
    create: () => ({ get: mockGet, post: mockPost }),
    isAxiosError,
  },
  isAxiosError,
}));

// Import AFTER vi.mock so the mocked axios is what the module captures.
import {
  cancelDeletion,
  deleteAccount,
  signIn,
  signOut,
  whoami,
} from "../auth";

afterEach(() => {
  mockGet.mockReset();
  mockPost.mockReset();
  isAxiosError.mockReset();
});

describe("signIn", () => {
  it("POSTs the credential to /auth/callback and returns the body", async () => {
    mockPost.mockResolvedValueOnce({
      data: {
        account_id: "acc-1",
        email: "alice@example.test",
        has_active_session: true,
      },
    });

    const res = await signIn("mock:alice@example.test");

    expect(mockPost).toHaveBeenCalledWith("/auth/callback", {
      credential: "mock:alice@example.test",
    });
    expect(res.account_id).toBe("acc-1");
    expect(res.has_active_session).toBe(true);
  });
});

describe("signOut", () => {
  it("POSTs to /auth/signout", async () => {
    mockPost.mockResolvedValueOnce({ data: {} });
    await signOut();
    expect(mockPost).toHaveBeenCalledWith("/auth/signout");
  });
});

describe("whoami", () => {
  it("returns the body on 200", async () => {
    mockGet.mockResolvedValueOnce({
      data: {
        account_id: "acc-1",
        email: "alice@example.test",
        has_active_session: true,
      },
    });
    const res = await whoami();
    expect(mockGet).toHaveBeenCalledWith("/auth/whoami");
    expect(res?.account_id).toBe("acc-1");
  });

  it("returns null on 401 (signed-out path is a normal state, not an error)", async () => {
    const err = Object.assign(new Error("unauthorized"), {
      response: { status: 401 },
      isAxiosError: true,
    });
    mockGet.mockRejectedValueOnce(err);
    isAxiosError.mockReturnValueOnce(true);

    const res = await whoami();
    expect(res).toBeNull();
  });

  it("re-throws non-401 errors", async () => {
    const err = Object.assign(new Error("boom"), {
      response: { status: 500 },
      isAxiosError: true,
    });
    mockGet.mockRejectedValueOnce(err);
    isAxiosError.mockReturnValueOnce(true);

    await expect(whoami()).rejects.toThrow(/boom/);
  });
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
