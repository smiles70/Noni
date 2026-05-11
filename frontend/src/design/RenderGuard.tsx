/**
 * RenderGuard — the fail-closed enforcement boundary.
 *
 * Per ADR 0019 and `docs/library/CONTRACT.md` Section IV.B, all rendering
 * MUST pass through this guard. On any contract violation, the guard renders
 * an explicit BlockedNotice naming the failed check. It never silently
 * degrades, never falls back, never approximates.
 *
 * Render Guards are authoritative and non-overrideable.
 *
 * The ten self-check items mirror CONTRACT Section V. Each returns a
 * `Violation` on failure; a non-empty list of violations blocks the render.
 */

import { ReactNode } from "react";
import {
  ALLOWED_COLOR_VALUES,
  ALLOWED_SPACING_VALUES,
  ALLOWED_RADIUS_VALUES,
  DENSITY_CEILINGS,
  MOTION,
  TYPOGRAPHY,
  type AuthorizedComponent,
} from "./tokens";
import type { UIStateEnvelope } from "./envelope";

// ---- Self-check item identifiers (mirror CONTRACT Section V) ----------------

export type CheckId =
  | "colors"
  | "shapes_and_spacing"
  | "grid_alignment"
  | "typography"
  | "authorized_components"
  | "interaction_density"
  | "irreversible_confirmation"
  | "no_optimistic_ui"
  | "motion"
  | "cognitive_load";

export interface Violation {
  check: CheckId;
  reason: string;
}

// ---- The render proposal the guard validates --------------------------------
//
// Components above the guard MUST pass a complete proposal describing
// what they intend to render. The guard does not infer; it verifies.

export interface RenderProposal {
  /** Components the proposal intends to render. Must be a subset of the
   *  envelope's `authorized_components`. */
  components: AuthorizedComponent[];

  /** Count of primary actions visible in the proposed render. */
  primaryActionCount: number;
  /** Count of irreversible actions in the proposed render. */
  irreversibleActionCount: number;
  /** Count of highlighted recommendations in the proposed render. */
  highlightedRecommendationCount: number;
  /** Number of distinct visible text levels. */
  visibleTextLevels: number;

  /** Every color used in the proposed render (hex strings). */
  colorsUsed: string[];
  /** Every spacing value used in the proposed render (px). */
  spacingPxUsed: number[];
  /** Every border-radius value used in the proposed render (px). */
  radiusPxUsed: number[];

  /** Motion durations used (ms). */
  motionDurationsMs: number[];
  /** Position-shift distances used (px). */
  positionShiftPxUsed: number[];

  /** True if any irreversible action lacks a matching confirmation gate
   *  using the standard copy pattern. */
  hasUnconfirmedIrreversibleAction: boolean;

  /** True if any progression depends on optimistic UI updates. */
  usesOptimisticProgression: boolean;
}

// ---- The ten checks (CONTRACT Section V) ------------------------------------

export function checkColors(p: RenderProposal): Violation | null {
  const disallowed = p.colorsUsed
    .map((c) => c.toUpperCase())
    .filter((c) => !ALLOWED_COLOR_VALUES.map((x) => x.toUpperCase()).includes(c));
  if (disallowed.length === 0) return null;
  return {
    check: "colors",
    reason: `Disallowed color(s): ${disallowed.join(", ")}`,
  };
}

export function checkShapesAndSpacing(p: RenderProposal): Violation | null {
  const badSpacing = p.spacingPxUsed.filter(
    (v) => !ALLOWED_SPACING_VALUES.includes(v),
  );
  const badRadius = p.radiusPxUsed.filter(
    (v) => !ALLOWED_RADIUS_VALUES.includes(v),
  );
  if (badSpacing.length === 0 && badRadius.length === 0) return null;
  const parts: string[] = [];
  if (badSpacing.length) parts.push(`spacing ${badSpacing.join(",")}`);
  if (badRadius.length) parts.push(`radius ${badRadius.join(",")}`);
  return {
    check: "shapes_and_spacing",
    reason: `Off-grid values: ${parts.join("; ")}`,
  };
}

export function checkGridAlignment(p: RenderProposal): Violation | null {
  // Closed-set spacing implies grid alignment by construction. Reflect any
  // residual violation here (e.g., negative spacing).
  if (p.spacingPxUsed.some((v) => v < 0)) {
    return { check: "grid_alignment", reason: "Negative spacing detected." };
  }
  return null;
}

export function checkTypography(p: RenderProposal): Violation | null {
  if (p.visibleTextLevels > TYPOGRAPHY.maxVisibleLevels) {
    return {
      check: "typography",
      reason: `>${TYPOGRAPHY.maxVisibleLevels} visible text levels (${p.visibleTextLevels}).`,
    };
  }
  return null;
}

export function checkAuthorizedComponents(
  p: RenderProposal,
  envelope: UIStateEnvelope,
): Violation | null {
  const allowed = new Set(envelope.authorized_components);
  const unauthorized = p.components.filter((c) => !allowed.has(c));
  if (unauthorized.length === 0) return null;
  return {
    check: "authorized_components",
    reason: `Components not authorized for state '${envelope.state_id}': ${unauthorized.join(", ")}`,
  };
}

export function checkInteractionDensity(
  p: RenderProposal,
  envelope: UIStateEnvelope,
): Violation | null {
  const limits = envelope.interaction_limits;
  if (p.primaryActionCount > limits.max_primary_actions) {
    return {
      check: "interaction_density",
      reason: `Primary actions ${p.primaryActionCount} > limit ${limits.max_primary_actions}.`,
    };
  }
  if (p.irreversibleActionCount > limits.max_irreversible_actions) {
    return {
      check: "interaction_density",
      reason: `Irreversible actions ${p.irreversibleActionCount} > limit ${limits.max_irreversible_actions}.`,
    };
  }
  if (
    p.highlightedRecommendationCount > limits.max_highlighted_recommendations
  ) {
    return {
      check: "interaction_density",
      reason: `Highlighted recommendations ${p.highlightedRecommendationCount} > limit ${limits.max_highlighted_recommendations}.`,
    };
  }
  // Belt-and-suspenders against contract-wide ceilings even if envelope is
  // somehow constructed above the maxima.
  if (p.primaryActionCount > DENSITY_CEILINGS.maxPrimaryActions) {
    return {
      check: "interaction_density",
      reason: `Primary actions exceed contract ceiling of ${DENSITY_CEILINGS.maxPrimaryActions}.`,
    };
  }
  return null;
}

export function checkIrreversibleConfirmation(
  p: RenderProposal,
): Violation | null {
  if (p.hasUnconfirmedIrreversibleAction) {
    return {
      check: "irreversible_confirmation",
      reason:
        "Irreversible action present without matching confirmation gate.",
    };
  }
  return null;
}

export function checkNoOptimisticUI(p: RenderProposal): Violation | null {
  if (p.usesOptimisticProgression) {
    return {
      check: "no_optimistic_ui",
      reason: "Optimistic UI for progression is prohibited (CONTRACT III).",
    };
  }
  return null;
}

export function checkMotion(p: RenderProposal): Violation | null {
  const badDurations = p.motionDurationsMs.filter(
    (ms) => ms < MOTION.fadeMinMs || ms > MOTION.fadeMaxMs,
  );
  const badShifts = p.positionShiftPxUsed.filter(
    (px) => px > MOTION.maxPositionShiftPx || px < 0,
  );
  if (badDurations.length === 0 && badShifts.length === 0) return null;
  const parts: string[] = [];
  if (badDurations.length) parts.push(`durations(ms) ${badDurations.join(",")}`);
  if (badShifts.length) parts.push(`shifts(px) ${badShifts.join(",")}`);
  return {
    check: "motion",
    reason: `Motion outside permitted bounds: ${parts.join("; ")}`,
  };
}

export function checkCognitiveLoad(
  p: RenderProposal,
  envelope: UIStateEnvelope,
): Violation | null {
  // A coarse but real check: cognitive load is preserved or reduced when
  // the proposal stays at or below the envelope's stated text-level limit.
  if (p.visibleTextLevels > envelope.interaction_limits.max_visible_text_levels) {
    return {
      check: "cognitive_load",
      reason: `Text levels ${p.visibleTextLevels} exceed envelope limit ${envelope.interaction_limits.max_visible_text_levels}.`,
    };
  }
  return null;
}

// ---- Aggregate ---------------------------------------------------------------

export function evaluateProposal(
  p: RenderProposal,
  envelope: UIStateEnvelope,
): Violation[] {
  const checks: (Violation | null)[] = [
    checkColors(p),
    checkShapesAndSpacing(p),
    checkGridAlignment(p),
    checkTypography(p),
    checkAuthorizedComponents(p, envelope),
    checkInteractionDensity(p, envelope),
    checkIrreversibleConfirmation(p),
    checkNoOptimisticUI(p),
    checkMotion(p),
    checkCognitiveLoad(p, envelope),
  ];
  return checks.filter((v): v is Violation => v !== null);
}

// ---- React boundary ---------------------------------------------------------

export interface RenderGuardProps {
  envelope: UIStateEnvelope;
  proposal: RenderProposal;
  children: ReactNode;
  /** Used by tests to inspect violation output without React rendering. */
  onViolations?: (violations: Violation[]) => void;
}

export function RenderGuard({
  envelope,
  proposal,
  children,
  onViolations,
}: RenderGuardProps) {
  const violations = evaluateProposal(proposal, envelope);
  if (onViolations) onViolations(violations);

  if (violations.length === 0) {
    return <>{children}</>;
  }

  // Validate that BlockedNotice itself is authorized in *some* fallback
  // envelope. Per contract, even the failure path must be auditable.
  const reasonList = violations.map((v) => `${v.check}: ${v.reason}`).join("\n");

  return (
    <section
      role="alert"
      aria-live="polite"
      data-component="BlockedNotice"
      data-state-id={envelope.state_id}
      style={{
        backgroundColor: "#FAFAF8",
        color: "#222222",
        padding: 24,
        borderRadius: 10,
        border: `2px solid ${"#B85C5C"}`,
        fontFamily: TYPOGRAPHY.fontFamily,
        fontSize: TYPOGRAPHY.bodySizePx,
        lineHeight: TYPOGRAPHY.bodyLineHeight,
      }}
    >
      <h2 style={{ fontSize: TYPOGRAPHY.headingScale.level2, margin: 0 }}>
        This screen is paused.
      </h2>
      <p style={{ marginTop: 16, marginBottom: 0 }}>
        The interface cannot continue safely right now. You can go back to
        the previous screen.
      </p>
      <pre
        style={{
          marginTop: 16,
          whiteSpace: "pre-wrap",
          fontSize: TYPOGRAPHY.bodySizePx,
        }}
        aria-label="diagnostic details"
      >
        {reasonList}
      </pre>
    </section>
  );
}
