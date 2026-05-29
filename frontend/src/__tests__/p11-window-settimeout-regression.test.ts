/**
 * P11/P23 — 1440-degree regression guard: no window.setTimeout in shared code.
 *
 * Gotcha: window.setTimeout crashes in Node.js/vitest because window is
 * undefined. globalThis is the ECMAScript standard universal global.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
// @ts-expect-error Vite raw import not in TypeScript declarations
import clientSource from "../api/client.ts?raw";

describe("P11/P23 regression guard", () => {
  beforeEach(() => {
    vi.resetModules();
  });

  it("source uses globalThis not window for timers", () => {
    expect(clientSource).toMatch(/globalThis\.setTimeout\s*\(/);
    expect(clientSource).toMatch(/globalThis\.clearTimeout\s*\(/);
    expect(clientSource).not.toMatch(/window\.setTimeout\s*\(/);
    expect(clientSource).not.toMatch(/window\.clearTimeout\s*\(/);
  });

  it("globalThis.setTimeout works with vitest fake timers", () => {
    vi.useFakeTimers();
    const controller = new AbortController();
    const id = globalThis.setTimeout(() => controller.abort(), 5000);
    vi.advanceTimersByTime(5000);
    expect(controller.signal.aborted).toBe(true);
    globalThis.clearTimeout(id);
    vi.useRealTimers();
  });

  it("request timeout cleanup works without window reference", async () => {
    if (typeof globalThis.fetch !== "function") {
      return; // Node < 18, skip
    }

    vi.useFakeTimers();
    const clearSpy = vi.spyOn(globalThis, "clearTimeout");

    const origFetch = globalThis.fetch;
    globalThis.fetch = vi.fn(() => Promise.reject(new Error("network"))) as unknown as typeof fetch;

    const { apiClient } = await import("../api/client.ts");
    try {
      await apiClient.get("/api/v1/health");
    } catch {
      // expected
    }

    expect(clearSpy).toHaveBeenCalled();

    globalThis.fetch = origFetch;
    clearSpy.mockRestore();
    vi.useRealTimers();
  });
});
