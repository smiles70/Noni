/**
 * RenderGuard contract tests.
 *
 * Each of the ten self-check items (CONTRACT Section V, ADR 0019) must
 * fail closed when violated and must pass when the proposal is compliant.
 *
 * Pure-logic tests against `evaluateProposal` — no React rendering needed,
 * so they run under any standard test runner (Vitest, Jest).
 */

import { describe, it, expect } from "vitest";
import {
  evaluateProposal,
  type RenderProposal,
} from "../RenderGuard";
import type { UIStateEnvelope } from "../envelope";

// ---- Fixtures ---------------------------------------------------------------

const envelope: UIStateEnvelope = {
  state_id: "test.state",
  authorized_components: ["Heading", "Body", "Button", "ConfirmDialog"],
  interaction_limits: {
    max_primary_actions: 3,
    max_irreversible_actions: 1,
    max_highlighted_recommendations: 1,
    max_visible_text_levels: 2,
  },
  layout_constraints: {
    grid_base_px: 8,
    allowed_spacing_px: [4, 8, 16, 24, 32, 48],
    spatial_stability: true,
    reflow_permitted: false,
  },
  transition_permissions: [],
};

const compliantProposal: RenderProposal = {
  components: ["Heading", "Body", "Button"],
  primaryActionCount: 2,
  irreversibleActionCount: 0,
  highlightedRecommendationCount: 1,
  visibleTextLevels: 2,
  colorsUsed: ["#F4F4F2", "#222222", "#4A6FA5"],
  spacingPxUsed: [8, 16, 24],
  radiusPxUsed: [8, 10],
  motionDurationsMs: [150],
  positionShiftPxUsed: [4],
  hasUnconfirmedIrreversibleAction: false,
  usesOptimisticProgression: false,
};

// ---- Compliance -------------------------------------------------------------

describe("RenderGuard — compliant proposal", () => {
  it("produces zero violations", () => {
    expect(evaluateProposal(compliantProposal, envelope)).toEqual([]);
  });
});

// ---- Each check fails closed under violation --------------------------------

describe("RenderGuard — each check fails closed", () => {
  it("check 1: disallowed color fails", () => {
    const p = { ...compliantProposal, colorsUsed: ["#FFFFFF"] };
    const v = evaluateProposal(p, envelope);
    expect(v.some((x) => x.check === "colors")).toBe(true);
  });

  it("check 2: off-grid spacing fails", () => {
    const p = { ...compliantProposal, spacingPxUsed: [7] };
    const v = evaluateProposal(p, envelope);
    expect(v.some((x) => x.check === "shapes_and_spacing")).toBe(true);
  });

  it("check 2: out-of-range radius fails", () => {
    const p = { ...compliantProposal, radiusPxUsed: [16] };
    const v = evaluateProposal(p, envelope);
    expect(v.some((x) => x.check === "shapes_and_spacing")).toBe(true);
  });

  it("check 3: negative spacing fails grid alignment", () => {
    // Note: also triggers shapes_and_spacing; we assert grid_alignment specifically.
    const p = { ...compliantProposal, spacingPxUsed: [-8] };
    const v = evaluateProposal(p, envelope);
    expect(v.some((x) => x.check === "grid_alignment")).toBe(true);
  });

  it("check 4: >3 visible text levels fails typography", () => {
    const p = { ...compliantProposal, visibleTextLevels: 4 };
    const v = evaluateProposal(p, envelope);
    expect(v.some((x) => x.check === "typography")).toBe(true);
  });

  it("check 5: unauthorized component fails", () => {
    const p = {
      ...compliantProposal,
      components: ["Heading", "Body", "Button", "Card"] as RenderProposal["components"],
    };
    // Card is not in envelope.authorized_components for this fixture.
    const v = evaluateProposal(p, envelope);
    expect(v.some((x) => x.check === "authorized_components")).toBe(true);
  });

  it("check 6: too many primary actions fails", () => {
    const p = { ...compliantProposal, primaryActionCount: 4 }; // limit is 3
    const v = evaluateProposal(p, envelope);
    expect(v.some((x) => x.check === "interaction_density")).toBe(true);
  });

  it("check 6: too many irreversible actions fails", () => {
    const p = { ...compliantProposal, irreversibleActionCount: 2 };
    const v = evaluateProposal(p, envelope);
    expect(v.some((x) => x.check === "interaction_density")).toBe(true);
  });

  it("check 7: irreversible action without confirmation fails", () => {
    const p = { ...compliantProposal, hasUnconfirmedIrreversibleAction: true };
    const v = evaluateProposal(p, envelope);
    expect(v.some((x) => x.check === "irreversible_confirmation")).toBe(true);
  });

  it("check 8: optimistic progression fails", () => {
    const p = { ...compliantProposal, usesOptimisticProgression: true };
    const v = evaluateProposal(p, envelope);
    expect(v.some((x) => x.check === "no_optimistic_ui")).toBe(true);
  });

  it("check 9: motion duration below 120ms fails", () => {
    const p = { ...compliantProposal, motionDurationsMs: [100] };
    const v = evaluateProposal(p, envelope);
    expect(v.some((x) => x.check === "motion")).toBe(true);
  });

  it("check 9: motion duration above 180ms fails", () => {
    const p = { ...compliantProposal, motionDurationsMs: [250] };
    const v = evaluateProposal(p, envelope);
    expect(v.some((x) => x.check === "motion")).toBe(true);
  });

  it("check 9: position shift > 8px fails", () => {
    const p = { ...compliantProposal, positionShiftPxUsed: [16] };
    const v = evaluateProposal(p, envelope);
    expect(v.some((x) => x.check === "motion")).toBe(true);
  });

  it("check 10: text levels exceed envelope limit fails cognitive_load", () => {
    // visibleTextLevels=3, envelope limit=2. Also fails typography? No — global cap is 3.
    const p = { ...compliantProposal, visibleTextLevels: 3 };
    const v = evaluateProposal(p, envelope);
    expect(v.some((x) => x.check === "cognitive_load")).toBe(true);
  });
});

// ---- Multiple violations accumulate -----------------------------------------

describe("RenderGuard — accumulates multiple violations", () => {
  it("returns all failing checks at once (does not short-circuit)", () => {
    const p: RenderProposal = {
      ...compliantProposal,
      colorsUsed: ["#FF0000"],
      spacingPxUsed: [7],
      visibleTextLevels: 5,
      usesOptimisticProgression: true,
    };
    const v = evaluateProposal(p, envelope);
    const checks = new Set(v.map((x) => x.check));
    expect(checks.has("colors")).toBe(true);
    expect(checks.has("shapes_and_spacing")).toBe(true);
    expect(checks.has("typography")).toBe(true);
    expect(checks.has("no_optimistic_ui")).toBe(true);
    expect(v.length).toBeGreaterThanOrEqual(4);
  });
});
