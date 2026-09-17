/**
 * WS-D: scroll-depth telemetry emits milestones once each, dedups,
 * and fails silently when the endpoint is unreachable.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

function setPage(height: number, viewportH: number, scrollY: number) {
  Object.defineProperty(document.documentElement, "scrollHeight", {
    value: height,
    configurable: true,
  });
  Object.defineProperty(window, "innerHeight", {
    value: viewportH,
    configurable: true,
  });
  Object.defineProperty(window, "scrollY", {
    value: scrollY,
    configurable: true,
  });
}

describe("trackScrollDepth", () => {
  // Fresh module per test — the dedup map in telemetryContract is
  // module-level and would otherwise suppress repeat keys across tests.
  let trackScrollDepth: typeof import("../scrollDepthTelemetry").trackScrollDepth;

  beforeEach(async () => {
    vi.resetModules();
    ({ trackScrollDepth } = await import("../scrollDepthTelemetry"));
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true }));
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("emits 25/50/90 milestones once each as depth passes", () => {
    setPage(4000, 1000, 0);
    const cleanup = trackScrollDepth("caregiver");

    setPage(4000, 1000, 900); // 30%
    window.dispatchEvent(new Event("scroll"));
    setPage(4000, 1000, 1800); // 60%
    window.dispatchEvent(new Event("scroll"));
    setPage(4000, 1000, 2850); // 95%
    window.dispatchEvent(new Event("scroll"));

    const calls = (fetch as ReturnType<typeof vi.fn>).mock.calls;
    const depths = calls.map((c) => JSON.parse(c[1].body).metadata.depth);
    expect(depths).toEqual([25, 50, 90]);
    for (const c of calls) {
      const body = JSON.parse(c[1].body);
      expect(body.event).toBe("marketing.scroll_depth");
      expect(body.metadata.page).toBe("caregiver");
      expect(c[0]).toBe("/api/v1/telemetry/marketing");
    }
    cleanup();
  });

  it("does not re-fire a threshold on repeated scrolls", () => {
    setPage(4000, 1000, 0);
    const cleanup = trackScrollDepth("for-communities");
    setPage(4000, 1000, 1200); // 40% — passes 25
    window.dispatchEvent(new Event("scroll"));
    window.dispatchEvent(new Event("scroll"));
    expect(fetch).toHaveBeenCalledTimes(1);
    cleanup();
  });

  it("reports full depth when the page fits the viewport", () => {
    setPage(800, 1000, 0);
    const cleanup = trackScrollDepth("caregiver");
    // No scroll possible — all three milestones fire on attach.
    expect(fetch).toHaveBeenCalledTimes(3);
    cleanup();
  });

  it("fails silently when the endpoint is unreachable", () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("down")));
    setPage(4000, 1000, 1200);
    const cleanup = trackScrollDepth("caregiver");
    expect(() => window.dispatchEvent(new Event("scroll"))).not.toThrow();
    cleanup();
  });
});
