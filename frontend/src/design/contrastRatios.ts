/**
 * Verified WCAG contrast ratios for Noni color tokens.
 *
 * Source of truth for which color pairs are permitted as text/background.
 * Computed via WebAIM contrast checker.
 *
 * Launch target: WCAG 2.1 AA (>= 4.5:1 normal text, >= 3:1 large text).
 * Future step-release target: AAA 7:1 for geragogy. Not a launch blocker.
 *
 * Any new color token MUST be added here with verified ratios before merge.
 */

import { COLORS } from "./tokens";

export interface ColorPair {
  foreground: string;
  background: string;
  ratio: number;
  aaPass: boolean;
  aaaPass: boolean;
  usage: string;
}

export const VERIFIED_CONTRAST_PAIRS: ColorPair[] = [
  // Body text — exceeds AAA on both surfaces
  {
    foreground: COLORS.textPrimary,
    background: COLORS.background,
    ratio: 13.5,
    aaPass: true,
    aaaPass: true,
    usage: "Body text on page background",
  },
  {
    foreground: COLORS.textPrimary,
    background: COLORS.surface,
    ratio: 15.4,
    aaPass: true,
    aaaPass: true,
    usage: "Body text on cards / elevated surfaces",
  },

  // Accent muted blue — AA floor
  {
    foreground: COLORS.accentMutedBlue,
    background: COLORS.background,
    ratio: 4.5,
    aaPass: true,
    aaaPass: false,
    usage: "NavBar buttons, secondary actions, focus rings",
  },
  {
    foreground: COLORS.accentMutedBlue,
    background: COLORS.surface,
    ratio: 4.8,
    aaPass: true,
    aaaPass: false,
    usage: "Links on card surfaces",
  },

  // Accent desaturated green — AA floor (Sprint 28 darkened to 4.3:1)
  {
    foreground: COLORS.accentDesatGreen,
    background: COLORS.background,
    ratio: 4.3,
    aaPass: true,
    aaaPass: false,
    usage: "Success indicators, progress labels (large text only)",
  },
  {
    foreground: COLORS.accentDesatGreen,
    background: COLORS.surface,
    ratio: 4.6,
    aaPass: true,
    aaaPass: false,
    usage: "Success states on cards",
  },

  // Error red — AA (Sprint 28 darkened from #B85C5C)
  {
    foreground: COLORS.errorConfirm,
    background: COLORS.background,
    ratio: 5.5,
    aaPass: true,
    aaaPass: false,
    usage: "Error text, destructive confirmations",
  },
  {
    foreground: COLORS.errorConfirm,
    background: COLORS.surface,
    ratio: 5.9,
    aaPass: true,
    aaaPass: false,
    usage: "Inline errors on form fields",
  },

  // Disabled — WCAG 1.4.3 explicitly exempts inactive UI components
  {
    foreground: COLORS.disabled,
    background: COLORS.background,
    ratio: 2.3,
    aaPass: false,
    aaaPass: false,
    usage: "Disabled controls — WCAG 1.4.3 exempt (inactive)",
  },
  {
    foreground: COLORS.disabled,
    background: COLORS.surface,
    ratio: 2.5,
    aaPass: false,
    aaaPass: false,
    usage: "Disabled controls on cards — WCAG 1.4.3 exempt (inactive)",
  },

  // Amber — RESTRICTED to non-text decorative use only per CONTRACT I.A
  {
    foreground: COLORS.accentMutedAmber,
    background: COLORS.background,
    ratio: 2.1,
    aaPass: false,
    aaaPass: false,
    usage: "DECORATIVE ONLY — never used as text. CONTRACT I.A restricted.",
  },
];
