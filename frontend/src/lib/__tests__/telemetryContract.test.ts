import { describe, expect, it } from "vitest";

import { ALLOWED_EVENTS, isAllowed, shouldEmit } from "../telemetryContract";

describe("telemetryContract — E72-B1", () => {
  it("suppresses an identical event inside the dedup window", () => {
    expect(shouldEmit("test.dedup", "k1")).toBe(true);
    expect(shouldEmit("test.dedup", "k1")).toBe(false);
  });

  it("treats different keys as distinct events", () => {
    expect(shouldEmit("test.keys", "a")).toBe(true);
    expect(shouldEmit("test.keys", "b")).toBe(true);
  });

  it("only permits contract events", () => {
    expect(isAllowed("lesson.completed")).toBe(true);
    expect(isAllowed("invented.event")).toBe(false);
  });

  it("includes the milestone set", () => {
    for (const m of [25, 50, 75, 100]) {
      expect(ALLOWED_EVENTS.has(`lesson.progress.${m}`)).toBe(true);
    }
  });
});
