/**
 * Axe-core configuration for contrast-focused audits.
 *
 * Targets WCAG 2.1 AA as the CI-enforced floor (4.5:1 normal text).
 * AAA 7:1 is documented as a future geragogy target in
 * `frontend/src/design/contrastRatios.ts` and tracked as a step-release
 * (not a launch blocker).
 */

export const CONTRAST_RULE_ID = "color-contrast";

/** Axe run options: audit ONLY the color-contrast rule. */
export const AXE_CONTRAST_OPTIONS = {
  runOnly: {
    type: "rule" as const,
    values: [CONTRAST_RULE_ID],
  },
};

/** AA threshold for CI-enforced baseline. */
export const AA_CONTRAST_RATIO = 4.5;

/** AAA threshold — documented aspiration, not CI-enforced at launch. */
export const AAA_CONTRAST_RATIO = 7.0;

/** Subset of axe violation shape we surface in CI logs. */
export interface ContrastViolation {
  id: string;
  description: string;
  nodes: Array<{
    target: string[];
    html: string;
    any: Array<{
      message: string;
      data?: {
        fgColor: string;
        bgColor: string;
        contrastRatio: number;
        fontSize: string;
        fontWeight: string;
      };
    }>;
  }>;
}
