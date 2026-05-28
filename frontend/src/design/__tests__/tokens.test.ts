/**
 * Enterprise design-token contract tests.
 *
 * Validates the closed set of permitted values per ADR 0019 / CONTRACT.md.
 * Any addition, removal, or mutation of a token value must be reflected
 * here and approved via ADR.
 */

import { describe, it, expect } from "vitest";
import {
  COLORS,
  SPACING,
  TYPOGRAPHY,
  RADIUS,
  MOTION,
  DENSITY_CEILINGS,
  AUTHORIZED_COMPONENTS,
  ALLOWED_COLOR_VALUES,
  ALLOWED_SPACING_VALUES,
  ALLOWED_RADIUS_VALUES,
  FOCUS,
  buildConfirmationCopy,
  CONFIRMATION_COPY_PATTERN,
} from "../tokens";

describe("COLORS", () => {
  it("contains only permitted hex values", () => {
    for (const [name, hex] of Object.entries(COLORS)) {
      expect(hex).toMatch(/^#[0-9A-Fa-f]{6}$/);
    }
  });

  it("exposes a frozen list of allowed values", () => {
    expect(ALLOWED_COLOR_VALUES.length).toBeGreaterThan(0);
    expect(Object.values(COLORS).sort()).toEqual(
      [...ALLOWED_COLOR_VALUES].sort()
    );
  });

  it("has no duplicate values", () => {
    const values = Object.values(COLORS);
    expect(new Set(values).size).toBe(values.length);
  });
});

describe("SPACING", () => {
  it("values match the contract-permitted set", () => {
    const permitted = new Set(ALLOWED_SPACING_VALUES);
    for (const v of Object.values(SPACING)) {
      expect(permitted.has(v)).toBe(true);
    }
  });

  it("exposes a frozen list of allowed values", () => {
    expect(ALLOWED_SPACING_VALUES.length).toBeGreaterThan(0);
    expect(Object.values(SPACING).sort((a, b) => a - b)).toEqual(
      [...ALLOWED_SPACING_VALUES].sort((a, b) => a - b)
    );
  });
});

describe("TYPOGRAPHY", () => {
  it("body size is at least 16px", () => {
    expect(TYPOGRAPHY.bodySizePx).toBeGreaterThanOrEqual(16);
  });

  it("line height is within 1.5–1.7", () => {
    expect(TYPOGRAPHY.bodyLineHeight).toBeGreaterThanOrEqual(1.5);
    expect(TYPOGRAPHY.bodyLineHeight).toBeLessThanOrEqual(1.7);
  });

  it("heading scale does not exceed 1.4x body size", () => {
    const max = Math.max(
      TYPOGRAPHY.headingScale.level1,
      TYPOGRAPHY.headingScale.level2,
      TYPOGRAPHY.headingScale.level3
    );
    expect(max / TYPOGRAPHY.bodySizePx).toBeLessThanOrEqual(1.4);
  });

  it("max visible levels is 3", () => {
    expect(TYPOGRAPHY.maxVisibleLevels).toBe(3);
  });
});

describe("RADIUS", () => {
  it("values are within 8–12px", () => {
    for (const v of Object.values(RADIUS)) {
      expect(v).toBeGreaterThanOrEqual(8);
      expect(v).toBeLessThanOrEqual(12);
    }
  });

  it("exposes a frozen list of allowed values", () => {
    expect(ALLOWED_RADIUS_VALUES.length).toBeGreaterThan(0);
    expect(Object.values(RADIUS).sort((a, b) => a - b)).toEqual(
      [...ALLOWED_RADIUS_VALUES].sort((a, b) => a - b)
    );
  });
});

describe("MOTION", () => {
  it("fade duration range is 120–180ms", () => {
    expect(MOTION.fadeMinMs).toBe(120);
    expect(MOTION.fadeMaxMs).toBe(180);
    expect(MOTION.defaultFadeMs).toBeGreaterThanOrEqual(MOTION.fadeMinMs);
    expect(MOTION.defaultFadeMs).toBeLessThanOrEqual(MOTION.fadeMaxMs);
  });

  it("position shift is <= 8px", () => {
    expect(MOTION.maxPositionShiftPx).toBeLessThanOrEqual(8);
  });

  it("only permits linear and ease-out", () => {
    expect(MOTION.allowedEasings).toEqual(["linear", "ease-out"]);
  });
});

describe("DENSITY_CEILINGS", () => {
  it("max primary actions is 5", () => {
    expect(DENSITY_CEILINGS.maxPrimaryActions).toBe(5);
  });

  it("max irreversible actions is 1", () => {
    expect(DENSITY_CEILINGS.maxIrreversibleActions).toBe(1);
  });

  it("max highlighted recommendations is 1", () => {
    expect(DENSITY_CEILINGS.maxHighlightedRecommendations).toBe(1);
  });

  it("max visible text levels matches typography cap", () => {
    expect(DENSITY_CEILINGS.maxVisibleTextLevels).toBe(TYPOGRAPHY.maxVisibleLevels);
  });
});

describe("AUTHORIZED_COMPONENTS", () => {
  it("contains the V1 component inventory", () => {
    expect(AUTHORIZED_COMPONENTS).toContain("Heading");
    expect(AUTHORIZED_COMPONENTS).toContain("Body");
    expect(AUTHORIZED_COMPONENTS).toContain("Button");
    expect(AUTHORIZED_COMPONENTS).toContain("Card");
    expect(AUTHORIZED_COMPONENTS).toContain("Field");
    expect(AUTHORIZED_COMPONENTS).toContain("List");
    expect(AUTHORIZED_COMPONENTS).toContain("Divider");
    expect(AUTHORIZED_COMPONENTS).toContain("Indicator");
    expect(AUTHORIZED_COMPONENTS).toContain("ConfirmDialog");
    expect(AUTHORIZED_COMPONENTS).toContain("PendingBanner");
    expect(AUTHORIZED_COMPONENTS).toContain("BlockedNotice");
  });

  it("has no duplicates", () => {
    expect(new Set(AUTHORIZED_COMPONENTS).size).toBe(AUTHORIZED_COMPONENTS.length);
  });
});

describe("FOCUS", () => {
  it("outline color is a permitted color", () => {
    expect(ALLOWED_COLOR_VALUES).toContain(FOCUS.outlineColor);
  });

  it("outline width is 2px", () => {
    expect(FOCUS.outlineWidthPx).toBe(2);
  });

  it("outline offset is 2px", () => {
    expect(FOCUS.outlineOffsetPx).toBe(2);
  });
});

describe("buildConfirmationCopy", () => {
  it("produces text matching the contract regex", () => {
    const copy = buildConfirmationCopy("your account access");
    expect(copy).toMatch(CONFIRMATION_COPY_PATTERN);
  });

  it("includes the change description", () => {
    const copy = buildConfirmationCopy("your password");
    expect(copy).toContain("your password");
  });

  it("always ends with the standard suffix", () => {
    const copy = buildConfirmationCopy("something");
    expect(copy).toMatch(/You can continue or go back\.$/);
  });
});
