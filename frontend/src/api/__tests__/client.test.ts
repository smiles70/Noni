/**
 * FetchClient / apiClient contract tests.
 *
 * Rack 3.2 of TEST-MATURITY-004: exercises the axios-compatible fetch
 * wrapper, path normalisation, request body handling, response parsing,
 * and token helpers.
 */
import { beforeEach, afterEach, describe, expect, it, vi } from "vitest";

vi.mock("../../lib/env", () => ({
  API_BASE_URL: "http://test.local",
}));

import {
  apiClient,
  API_BASE_URL,
  clearMagicToken,
  clearMockToken,
  MAGIC_TOKEN_KEY,
  MOCK_TOKEN_KEY,
  setMagicToken,
  setMockToken,
} from "../client";

function makeResponse(
  body: unknown,
  status = 200,
  extraHeaders?: Record<string, string>,
) {
  const headers = new Headers({
    "content-type": "application/json",
    ...extraHeaders,
  });
  return new Response(JSON.stringify(body), {
    status,
    statusText: "OK",
    headers,
  });
}

function lastFetchCall() {
  const calls = (globalThis.fetch as ReturnType<typeof vi.fn>).mock.calls;
  return calls[calls.length - 1] as [string, RequestInit | undefined];
}

describe("apiClient", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => makeResponse({ ok: true })),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("GET returns parsed JSON", async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      makeResponse({ items: [1, 2] }),
    );
    const resp = await apiClient.get<{ items: number[] }>("/api/lessons");
    expect(resp.data).toEqual({ items: [1, 2] });
    expect(resp.status).toBe(200);
  });

  it("normalises legacy /api/ paths to /api/v1", async () => {
    await apiClient.get("/api/lessons");
    const [url] = lastFetchCall();
    expect(url).toBe("http://test.local/api/v1/lessons");
  });

  it("normalises /auth paths to /api/v1/auth", async () => {
    await apiClient.get("/auth/config");
    const [url] = lastFetchCall();
    expect(url).toBe("http://test.local/api/v1/auth/config");
  });

  it("normalises /me paths to /api/v1/me", async () => {
    await apiClient.get("/me/delete");
    const [url] = lastFetchCall();
    expect(url).toBe("http://test.local/api/v1/me/delete");
  });

  it("keeps fully qualified URLs unchanged", async () => {
    await apiClient.get("https://example.com/health");
    const [url] = lastFetchCall();
    expect(url).toBe("https://example.com/health");
  });

  it("keeps already-prefixed /api/v1 URLs unchanged", async () => {
    await apiClient.get("/api/v1/lessons");
    const [url] = lastFetchCall();
    expect(url).toBe("http://test.local/api/v1/lessons");
  });

  it("POST serialises the body and sets Content-Type", async () => {
    await apiClient.post("/me/delete", { reason: "test" });
    const [, init] = lastFetchCall();
    expect(init?.method).toBe("POST");
    expect(init?.body).toBe(JSON.stringify({ reason: "test" }));
    expect((init?.headers as Record<string, string>)["Content-Type"]).toBe(
      "application/json",
    );
  });

  it("PUT, PATCH and DELETE send the correct method", async () => {
    await apiClient.put("/items/1", { a: 1 });
    expect(lastFetchCall()[1]?.method).toBe("PUT");

    await apiClient.patch("/items/1", { a: 2 });
    expect(lastFetchCall()[1]?.method).toBe("PATCH");

    await apiClient.delete("/items/1");
    expect(lastFetchCall()[1]?.method).toBe("DELETE");
  });

  it("returns a blob when responseType is blob", async () => {
    const blob = new Blob(["hello"]);
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      new Response(blob, { status: 200, statusText: "OK" }),
    );
    const resp = await apiClient.get("/export", { responseType: "blob" });
    // jsdom Response.blob() returns a cross-realm Blob; check shape instead.
    expect((resp.data as Blob).constructor.name).toBe("Blob");
    expect((resp.data as Blob).size).toBeGreaterThan(0);
  });

  it("uses validateStatus to decide success", async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      makeResponse({ detail: "not found" }, 404),
    );
    const resp = await apiClient.get("/items/1", {
      validateStatus: () => true,
    });
    expect(resp.status).toBe(404);
  });

  it("throws on non-OK responses with response attached", async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      makeResponse({ detail: "boom" }, 400),
    );
    await expect(apiClient.get("/items/1", { retry: false })).rejects.toThrow(
      "Request failed",
    );

    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      makeResponse({ detail: "boom" }, 400),
    );
    try {
      await apiClient.get("/items/1", { retry: false });
    } catch (err) {
      expect((err as { response?: { status: number } }).response?.status).toBe(
        400,
      );
    }
  });

  it("allows request interceptors to modify config", async () => {
    const id = apiClient.interceptors.request.use((config) => ({
      ...config,
      headers: { ...config.headers, "X-Custom": "yes" },
    }));
    await apiClient.get("/api/v1/lessons");
    const [, init] = lastFetchCall();
    expect((init?.headers as Record<string, string>)["X-Custom"]).toBe("yes");
    apiClient.interceptors.request.eject(id);
  });
});

describe("token helpers", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it("setMockToken writes the mock key", () => {
    setMockToken("user@example.com");
    expect(localStorage.getItem(MOCK_TOKEN_KEY)).toBe("mock:user@example.com");
  });

  it("clearMockToken removes the mock key", () => {
    setMockToken("user@example.com");
    clearMockToken();
    expect(localStorage.getItem(MOCK_TOKEN_KEY)).toBeNull();
  });

  it("setMagicToken writes the magic key", () => {
    setMagicToken("did:token");
    expect(localStorage.getItem(MAGIC_TOKEN_KEY)).toBe("did:token");
  });

  it("clearMagicToken removes the magic key", () => {
    setMagicToken("did:token");
    clearMagicToken();
    expect(localStorage.getItem(MAGIC_TOKEN_KEY)).toBeNull();
  });
});

describe("API_BASE_URL re-export", () => {
  it("re-exports the base URL from env", () => {
    expect(API_BASE_URL).toBe("http://test.local");
  });
});
