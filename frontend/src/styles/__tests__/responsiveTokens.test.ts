/**
 * Enterprise responsive-token contract tests.
 *
 * Validates geragogy-first responsive values: minimum touch targets,
 * readable type scales, and spacing consistency across breakpoints.
 */

import { describe, it, expect } from "vitest";
import {
  MIN_TOUCH_TARGET,
  TYPE_SCALE,
  MAX_CONTENT_WIDTH,
  SPACING,
} from "../responsiveTokens";

describe("MIN_TOUCH_TARGET", () => {
  it("mobile is at least 48px (WCAG 2.5.5)", () => {
    expect(MIN_TOUCH_TARGET.mobile).toBeGreaterThanOrEqual(48);
  });

  it("never drops below 40px", () => {
    for (const v of Object.values(MIN_TOUCH_TARGET)) {
      expect(v).toBeGreaterThanOrEqual(40);
    }
  });

  it("decreases or stays flat as viewport grows", () => {
    expect(MIN_TOUCH_TARGET.tablet).toBeLessThanOrEqual(
      MIN_TOUCH_TARGET.mobile
    );
    expect(MIN_TOUCH_TARGET.desktop).toBeLessThanOrEqual(
      MIN_TOUCH_TARGET.tablet
    );
    expect(MIN_TOUCH_TARGET.wide).toBeLessThanOrEqual(
      MIN_TOUCH_TARGET.desktop
    );
  });
});

describe("TYPE_SCALE", () => {
  it("body size is never below 16px", () => {
    for (const bp of Object.values(TYPE_SCALE)) {
      expect(bp.body).toBeGreaterThanOrEqual(16);
    }
  });

  it("small text is never below 12px", () => {
    for (const bp of Object.values(TYPE_SCALE)) {
      expect(bp.small).toBeGreaterThanOrEqual(12);
    }
  });

  it("h1 is the largest variant per breakpoint", () => {
    for (const bp of Object.values(TYPE_SCALE)) {
      expect(bp.h1).toBeGreaterThanOrEqual(bp.h2);
      expect(bp.h2).toBeGreaterThanOrEqual(bp.h3);
      expect(bp.h3).toBeGreaterThanOrEqual(bp.body);
    }
  });

  it("mobile h1 is <= 40px (geragogy cap)", () => {
    expect(TYPE_SCALE.mobile.h1).toBeLessThanOrEqual(40);
  });
});

describe("MAX_CONTENT_WIDTH", () => {
  it("mobile is 100%", () => {
    expect(MAX_CONTENT_WIDTH.mobile).toBe("100%");
  });

  it("increases with viewport size", () => {
    const toPx = (s: string) => parseInt(s, 10);
    expect(toPx(MAX_CONTENT_WIDTH.tablet)).toBeLessThan(
      toPx(MAX_CONTENT_WIDTH.desktop)
    );
    expect(toPx(MAX_CONTENT_WIDTH.desktop)).toBeLessThanOrEqual(
      toPx(MAX_CONTENT_WIDTH.wide)
    );
  });
});

describe("SPACING", () => {
  it("xs is always 8px", () => {
    for (const bp of Object.values(SPACING)) {
      expect(bp.xs).toBe(8);
    }
  });

  it("scales increase with breakpoint", () => {
    for (const key of ["sm", "md", "lg", "xl"] as const) {
      expect(SPACING.tablet[key]).toBeGreaterThanOrEqual(
        SPACING.mobile[key]
      );
      expect(SPACING.desktop[key]).toBeGreaterThanOrEqual(
        SPACING.tablet[key]
      );
      expect(SPACING.wide[key]).toBeGreaterThanOrEqual(
        SPACING.desktop[key]
      );
    }
  });

  it("xl never exceeds 48px", () => {
    for (const bp of Object.values(SPACING)) {
      expect(bp.xl).toBeLessThanOrEqual(48);
    }
  });
});
