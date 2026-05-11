/**
 * Design tokens — the closed set, enforced by ADR 0019.
 *
 * These are the ONLY permitted values for color, spacing, type, radius,
 * and motion in the system. Any hex literal, spacing value, or motion
 * duration outside this file is a contract violation and MUST be rejected
 * by Render Guards (see `RenderGuard.tsx`).
 *
 * Source of truth: `docs/library/CONTRACT.md` (Section I).
 *
 * DO NOT ADD VALUES TO THIS FILE WITHOUT A NEW ADR.
 */

// ---- Color (CONTRACT Section I.A) -------------------------------------------

export const COLORS = {
  // Neutrals
  background: "#F4F4F2",
  surface: "#FAFAF8",
  textPrimary: "#222222",

  // Accents (non-urgent)
  accentMutedBlue: "#4A6FA5",
  accentDesatGreen: "#5A7D6C",
  accentMutedAmber: "#C9A24D",

  // Restricted (functional use only)
  errorConfirm: "#B85C5C",
  disabled: "#B0B0B0",
} as const;

export type ColorToken = keyof typeof COLORS;

/** The complete, closed set of permitted color hex values. */
export const ALLOWED_COLOR_VALUES: readonly string[] = Object.freeze(
  Object.values(COLORS),
);

// ---- Spacing (CONTRACT Section I.B) -----------------------------------------

/**
 * 8px base grid. Permitted spacing values: 4 / 8 / 16 / 24 / 32 / 48.
 * No arbitrary spacing values permitted.
 */
export const SPACING = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const;

export type SpacingToken = keyof typeof SPACING;

export const ALLOWED_SPACING_VALUES: readonly number[] = Object.freeze(
  Object.values(SPACING),
);

export const GRID_BASE_PX = 8 as const;

// ---- Typography (CONTRACT Section I.C) --------------------------------------

export const TYPOGRAPHY = {
  fontFamily:
    'Inter, "Source Sans 3", system-ui, -apple-system, BlinkMacSystemFont, sans-serif',

  // Base size (minimum 16px per contract).
  bodySizePx: 16,
  bodyLineHeight: 1.6, // within 1.5–1.7

  // Heading scale: ≤1.4× body size.
  // Three visible levels max.
  headingScale: {
    level1: 22, // ≈1.375×
    level2: 19, // ≈1.1875×
    level3: 17, // ≈1.0625×
  },

  // Max 3 levels visible simultaneously.
  maxVisibleLevels: 3,
} as const;

// ---- Shape & Radius (CONTRACT Section I.B) ----------------------------------

/** Rectangles with rounded corners (8–12px radius). */
export const RADIUS = {
  sm: 8,
  md: 10,
  lg: 12,
} as const;

export const ALLOWED_RADIUS_VALUES: readonly number[] = Object.freeze(
  Object.values(RADIUS),
);

// ---- Motion (CONTRACT Section I.G) ------------------------------------------

/**
 * Opacity fades 120–180ms. Position transitions ≤8px. Linear or ease-out.
 * No bounce, spring, elastic. No concurrent region animations.
 */
export const MOTION = {
  fadeMinMs: 120,
  fadeMaxMs: 180,
  defaultFadeMs: 150,
  maxPositionShiftPx: 8,
  allowedEasings: ["linear", "ease-out"] as const,
} as const;

// ---- Focus (CONTRACT Section II) --------------------------------------------

export const FOCUS = {
  outlineWidthPx: 2,
  outlineOffsetPx: 2,
  outlineColor: COLORS.accentMutedBlue,
} as const;

// ---- Interaction density ceilings (CONTRACT Section I.F) --------------------

export const DENSITY_CEILINGS = {
  maxPrimaryActions: 5,
  maxIrreversibleActions: 1,
  maxHighlightedRecommendations: 1,
  maxVisibleTextLevels: TYPOGRAPHY.maxVisibleLevels,
} as const;

// ---- V1 Component inventory (CONTRACT Section I.D) --------------------------

export const AUTHORIZED_COMPONENTS = [
  "Heading",
  "Body",
  "Button",
  "Card",
  "Field",
  "List",
  "Divider",
  "Indicator",
  "ConfirmDialog",
  "PendingBanner",
  "BlockedNotice",
] as const;

export type AuthorizedComponent = (typeof AUTHORIZED_COMPONENTS)[number];

// ---- Confirmation copy pattern (CONTRACT Section III) -----------------------

/**
 * Standard confirmation phrasing:
 *   "This will change [X]. You can continue or go back."
 *
 * Render Guards verify any ConfirmDialog uses this exact pattern.
 */
export const CONFIRMATION_COPY_PATTERN =
  /^This will change [^.]+\. You can continue or go back\.$/;

export function buildConfirmationCopy(changeDescription: string): string {
  return `This will change ${changeDescription}. You can continue or go back.`;
}
