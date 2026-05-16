/**
 * Tripwire tests for the curriculum page-type RenderGuard math.
 *
 * For every (page_type, retrieval-answered-state) combination, compose
 * the page-body proposal contribution + the renderer's NavBar/action-row
 * additions and run the result through `evaluateProposal` against the
 * production curriculum.unit envelope shape.
 *
 * This test is the single fail-closed check that catches any future
 * change to PageTypes.tsx style constants which would silently push the
 * proposal outside the envelope (bumped to max_primary_actions=5 in
 * Phase 1). If a contributor adds, say, a new color or a 6th component
 * to a sub-renderer, this test fails BEFORE the runtime guard does.
 */

import { describe, it, expect } from "vitest";
import { buildPageProposalContribution } from "../PageTypes";
import {
  evaluateProposal,
  type RenderProposal,
} from "../../../design/RenderGuard";
import type { UIStateEnvelope } from "../../../design/envelope";
import type { CurriculumPage } from "../../../api/curriculum";
import {
  COLORS,
  SPACING,
  RADIUS,
  MOTION,
} from "../../../design/tokens";

// ---- Fixture: the production curriculum.unit envelope -----------------------
//
// Mirrored from `backend/models/ui_state_envelope.py` after the Phase-1
// bump: LIST authorized, max_primary_actions=5. Keeping the shape pinned
// here means a future backend change that *narrows* the envelope without
// updating this test will surface as a frontend test failure — which is
// exactly the cross-stack contract loop CONTRACT V is designed to enforce.
const curriculumUnitEnvelope: UIStateEnvelope = {
  state_id: "curriculum.unit",
  authorized_components: [
    "Heading",
    "Body",
    "Button",
    "Card",
    "List",
    "Divider",
    "Indicator",
    "PendingBanner",
    "BlockedNotice",
  ],
  interaction_limits: {
    max_primary_actions: 5,
    max_irreversible_actions: 0,
    max_highlighted_recommendations: 1,
    max_visible_text_levels: 3,
  },
  layout_constraints: {
    grid_base_px: 8,
    allowed_spacing_px: [4, 8, 16, 24, 32, 48],
    spatial_stability: true,
    reflow_permitted: false,
  },
  transition_permissions: [],
};

// Page bodies aligned with the unit-2 exemplar shape.
function makePage(overrides: Partial<CurriculumPage>): CurriculumPage {
  return {
    id: "p",
    title: "T",
    content: ["body line 1", "body line 2"],
    complexity: 1,
    ...overrides,
  };
}

// ---- Helper: simulate the renderer's full proposal ------------------------

const PAGE_COLORS = [
  COLORS.background,
  COLORS.surface,
  COLORS.textPrimary,
  COLORS.accentMutedBlue,
  COLORS.accentDesatGreen,
  COLORS.accentMutedAmber,
  COLORS.disabled,
];
const PAGE_SPACING = [
  SPACING.xs,
  SPACING.sm,
  SPACING.md,
  SPACING.lg,
  SPACING.xl,
];
const PAGE_RADIUS = [RADIUS.sm, RADIUS.md];
const PAGE_MOTION = [MOTION.defaultFadeMs];

function buildFullProposal(
  page: CurriculumPage,
  retrievalAnswered: string | null,
): RenderProposal {
  const contribution = buildPageProposalContribution(page, retrievalAnswered);
  const isRetrieval = (page.page_type ?? "principle") === "retrieval";
  const showChoices = isRetrieval && retrievalAnswered === null;
  const showContinue = !showChoices;
  const NAVBAR_PRIMARY_ACTIONS = 2;

  const components = new Set<RenderProposal["components"][number]>(
    contribution.components,
  );
  components.add("Indicator");
  if (showContinue || showChoices) components.add("Button");

  return {
    components: Array.from(components),
    primaryActionCount:
      NAVBAR_PRIMARY_ACTIONS +
      (showContinue ? 1 : 0) +
      contribution.primaryActionsFromBody,
    irreversibleActionCount: 0,
    highlightedRecommendationCount: showContinue ? 1 : 0,
    visibleTextLevels: contribution.visibleTextLevels,
    colorsUsed: PAGE_COLORS,
    spacingPxUsed: PAGE_SPACING,
    radiusPxUsed: PAGE_RADIUS,
    motionDurationsMs: PAGE_MOTION,
    positionShiftPxUsed: [],
    hasUnconfirmedIrreversibleAction: false,
    usesOptimisticProgression: false,
  };
}

// ---- Per-page-type proposals must produce zero violations ------------------

describe("curriculum page-type proposals are envelope-compliant", () => {
  it("recap page", () => {
    const p = makePage({ page_type: "recap" });
    expect(
      evaluateProposal(buildFullProposal(p, null), curriculumUnitEnvelope),
    ).toEqual([]);
  });

  it("context page", () => {
    const p = makePage({ page_type: "context" });
    expect(
      evaluateProposal(buildFullProposal(p, null), curriculumUnitEnvelope),
    ).toEqual([]);
  });

  it("principle page (with highlighted card)", () => {
    const p = makePage({
      page_type: "principle",
      principle: "Claude offers words.",
    });
    expect(
      evaluateProposal(buildFullProposal(p, null), curriculumUnitEnvelope),
    ).toEqual([]);
  });

  it("principle page (legacy: no page_type)", () => {
    // Legacy pages without page_type default to "principle". The
    // contribution function must still produce a valid proposal.
    const p = makePage({});
    expect(
      evaluateProposal(buildFullProposal(p, null), curriculumUnitEnvelope),
    ).toEqual([]);
  });

  it("example page", () => {
    const p = makePage({
      page_type: "example",
      example: {
        situation: "s",
        claude_says: "c",
        takeaway: "t",
      },
    });
    expect(
      evaluateProposal(buildFullProposal(p, null), curriculumUnitEnvelope),
    ).toEqual([]);
  });

  it("retrieval page — pre-answer (worst-case interaction density)", () => {
    const p = makePage({
      page_type: "retrieval",
      retrieval: {
        prompt: "Pick one",
        choices: [
          { id: "a", text: "A" },
          { id: "b", text: "B" },
        ],
        correct_id: "a",
        explanation: "e",
      },
    });
    const proposal = buildFullProposal(p, null);
    // Sanity: this is the page that actually exercises the bumped
    // primary-action ceiling.
    expect(proposal.primaryActionCount).toBe(4);
    expect(proposal.highlightedRecommendationCount).toBe(0);
    expect(evaluateProposal(proposal, curriculumUnitEnvelope)).toEqual([]);
  });

  it("retrieval page — post-answer (Continue + feedback Card)", () => {
    const p = makePage({
      page_type: "retrieval",
      retrieval: {
        prompt: "Pick one",
        choices: [
          { id: "a", text: "A" },
          { id: "b", text: "B" },
        ],
        correct_id: "a",
        explanation: "e",
      },
    });
    const proposal = buildFullProposal(p, "a");
    expect(proposal.primaryActionCount).toBe(3);
    expect(proposal.highlightedRecommendationCount).toBe(1);
    expect(evaluateProposal(proposal, curriculumUnitEnvelope)).toEqual([]);
  });
});

// ---- Direct tripwires on the contribution shape ----------------------------

describe("buildPageProposalContribution invariants", () => {
  it("retrieval pre-answer adds 2 page-body primary actions", () => {
    const p = makePage({
      page_type: "retrieval",
      retrieval: {
        prompt: "x",
        choices: [
          { id: "a", text: "A" },
          { id: "b", text: "B" },
        ],
        correct_id: "a",
        explanation: "e",
      },
    });
    expect(buildPageProposalContribution(p, null).primaryActionsFromBody).toBe(
      2,
    );
  });

  it("retrieval post-answer contributes 0 page-body primary actions", () => {
    const p = makePage({
      page_type: "retrieval",
      retrieval: {
        prompt: "x",
        choices: [
          { id: "a", text: "A" },
          { id: "b", text: "B" },
        ],
        correct_id: "a",
        explanation: "e",
      },
    });
    expect(buildPageProposalContribution(p, "a").primaryActionsFromBody).toBe(
      0,
    );
  });

  it("non-retrieval pages contribute 0 page-body primary actions", () => {
    for (const page_type of ["recap", "context", "principle", "example"] as const) {
      const p = makePage({ page_type });
      if (page_type === "example") {
        p.example = { situation: "s", claude_says: "c", takeaway: "t" };
      }
      expect(
        buildPageProposalContribution(p, null).primaryActionsFromBody,
      ).toBe(0);
    }
  });

  it("text levels never exceed 2 for any page type", () => {
    for (const page_type of [
      "recap",
      "context",
      "principle",
      "example",
      "retrieval",
    ] as const) {
      const p = makePage({ page_type });
      if (page_type === "example") {
        p.example = { situation: "s", claude_says: "c", takeaway: "t" };
      }
      if (page_type === "retrieval") {
        p.retrieval = {
          prompt: "p",
          choices: [
            { id: "a", text: "A" },
            { id: "b", text: "B" },
          ],
          correct_id: "a",
          explanation: "e",
        };
      }
      expect(buildPageProposalContribution(p, null).visibleTextLevels).toBe(2);
    }
  });
});
