// PURE DATA — NO SIDE EFFECTS
// Geragogy-first responsive design tokens.
// These complement (do not replace) design/tokens.ts.

export const MIN_TOUCH_TARGET = {
  mobile: 48,
  tablet: 44,
  desktop: 40,
  wide: 40,
} as const;

export const TYPE_SCALE = {
  mobile: { base: 18, h1: 28, h2: 24, h3: 20, body: 18, small: 14 },
  tablet: { base: 16, h1: 32, h2: 26, h3: 22, body: 16, small: 13 },
  desktop: { base: 16, h1: 36, h2: 28, h3: 24, body: 16, small: 12 },
  wide: { base: 16, h1: 40, h2: 32, h3: 24, body: 16, small: 12 },
} as const;

export const MAX_CONTENT_WIDTH = {
  mobile: "100%",
  tablet: "720px",
  desktop: "960px",
  wide: "1080px",
} as const;

export const SPACING = {
  mobile: { xs: 8, sm: 12, md: 16, lg: 24, xl: 32 },
  tablet: { xs: 8, sm: 16, md: 20, lg: 28, xl: 36 },
  desktop: { xs: 8, sm: 16, md: 24, lg: 32, xl: 48 },
  wide: { xs: 8, sm: 16, md: 24, lg: 32, xl: 48 },
} as const;

export type BreakpointKey = keyof typeof SPACING;
export type SpacingKey = keyof typeof SPACING.mobile;
