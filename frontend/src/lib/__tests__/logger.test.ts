/**
 * Structured logger contract tests.
 *
 * Rack 3.2 of TEST-MATURITY-004: exercises level routing and context
 * payload shape.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { logger } from "../logger";

let spies: {
  info: ReturnType<typeof vi.spyOn>;
  warn: ReturnType<typeof vi.spyOn>;
  error: ReturnType<typeof vi.spyOn>;
};

beforeEach(() => {
  spies = {
    info: vi.spyOn(console, "info").mockImplementation(() => undefined),
    warn: vi.spyOn(console, "warn").mockImplementation(() => undefined),
    error: vi.spyOn(console, "error").mockImplementation(() => undefined),
  };
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("logger", () => {
  it("routes info level to console.info with context", () => {
    logger.info("hello", { user: 1 });
    expect(spies.info).toHaveBeenCalledTimes(1);
    expect(spies.info.mock.calls[0][0]).toEqual({
      msg: "hello",
      ctx: { user: 1 },
    });
  });

  it("emits plain message when no context provided", () => {
    logger.warn("plain");
    expect(spies.warn).toHaveBeenCalledWith("plain");
  });

  it("calls all four level methods without throwing", () => {
    expect(() => {
      logger.debug("d");
      logger.info("i");
      logger.warn("w");
      logger.error("e");
    }).not.toThrow();
    expect(spies.info).toHaveBeenCalledWith("i");
    expect(spies.warn).toHaveBeenCalledWith("w");
    expect(spies.error).toHaveBeenCalledWith("e");
  });
});
