/**
 * Page-type sub-renderers + per-page-type RenderProposal builder.
 *
 * Curriculum-expansion Phase 1 (CONTRACT IV / ADR 0019):
 *   The curriculum.unit envelope authorizes Heading, Body, Button, Card,
 *   List, Divider, Indicator, PendingBanner, BlockedNotice. These
 *   sub-renderers compose ONLY from that set. Each page-type renders
 *   the page-body region (everything between the indicator and the
 *   bottom action row); the parent CurriculumRenderer owns the NavBar,
 *   the lesson/page indicator, and the action row (Continue or, for
 *   retrieval pre-answer, the two choice buttons).
 *
 * Why a single file for all five page types:
 *   They share style constants (PARA, CARD, etc.) and are tiny — a
 *   one-file home keeps the proposal accounting (`buildPageProposal`)
 *   adjacent to the JSX it describes, so a future author who adds a
 *   sixth page type cannot forget to update the proposal contribution.
 *
 * Why `buildPageProposal` is pure:
 *   The unit test for it composes each page-type's proposal with the
 *   NavBar contribution and asserts `evaluateProposal(...) === []`
 *   against the real curriculum.unit envelope shape. That test is the
 *   tripwire for any future style edit that would silently bust the
 *   RenderGuard at runtime.
 */
import { CSSProperties, ReactNode } from "react";

import type { CurriculumPage, RetrievalBlock, ExampleBlock } from "../../api/curriculum";
import {
  COLORS,
  SPACING,
  TYPOGRAPHY,
  RADIUS,
  MOTION,
  type AuthorizedComponent,
} from "../../design/tokens";

// ---- Shared style objects (all values are tokens) --------------------------

const H1: CSSProperties = {
  fontSize: TYPOGRAPHY.headingScale.level1,
  marginTop: 0,
  marginBottom: SPACING.md,
  color: COLORS.textPrimary,
  fontFamily: TYPOGRAPHY.fontFamily,
  lineHeight: TYPOGRAPHY.bodyLineHeight,
};

const PARA: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  lineHeight: TYPOGRAPHY.bodyLineHeight,
  fontFamily: TYPOGRAPHY.fontFamily,
  color: COLORS.textPrimary,
  marginTop: 0,
  marginBottom: SPACING.md,
};

const CARD: CSSProperties = {
  backgroundColor: COLORS.surface,
  border: `2px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.md,
  padding: SPACING.lg,
  marginTop: SPACING.md,
  marginBottom: SPACING.md,
};

const CARD_FEEDBACK_CORRECT: CSSProperties = {
  ...CARD,
  borderColor: COLORS.accentDesatGreen,
};

const CARD_FEEDBACK_INCORRECT: CSSProperties = {
  ...CARD,
  borderColor: COLORS.accentMutedAmber,
};

const CARD_HEADER: CSSProperties = {
  ...PARA,
  marginBottom: SPACING.sm,
  fontWeight: 600,
};

const CARD_BODY: CSSProperties = {
  ...PARA,
  marginBottom: 0,
  whiteSpace: "pre-wrap",
};

const DIVIDER: CSSProperties = {
  border: "none",
  borderTop: `1px solid ${COLORS.disabled}`,
  marginTop: SPACING.md,
  marginBottom: SPACING.md,
};

// ---- Sub-renderers ---------------------------------------------------------
//
// Every sub-renderer returns the same shape: a fragment beginning with
// the page title (h1) and followed by body content. The parent renders
// NavBar above and the action row below; sub-renderers never reach
// outside their region.

function renderContent(content: string[]): ReactNode {
  return content.map((line, i) => (
    <p key={i} style={PARA} data-component="Body">
      {line}
    </p>
  ));
}

export function RecapPage({ page }: { page: CurriculumPage }) {
  return (
    <section aria-label="Recap" data-page-type="recap">
      <h1 style={H1} data-component="Heading">
        {page.title}
      </h1>
      {renderContent(page.content)}
    </section>
  );
}

export function ContextPage({ page }: { page: CurriculumPage }) {
  return (
    <section aria-label="Context" data-page-type="context">
      <h1 style={H1} data-component="Heading">
        {page.title}
      </h1>
      {renderContent(page.content)}
    </section>
  );
}

export function PrinciplePage({ page }: { page: CurriculumPage }) {
  return (
    <section aria-label="Principle" data-page-type="principle">
      <h1 style={H1} data-component="Heading">
        {page.title}
      </h1>
      {page.principle ? (
        <div style={CARD} data-component="Card" aria-label="The principle">
          <p style={CARD_HEADER}>The rule:</p>
          <p style={{ ...PARA, marginBottom: 0 }} data-component="Body">
            {page.principle}
          </p>
        </div>
      ) : null}
      {renderContent(page.content)}
    </section>
  );
}

export function ExamplePage({
  page,
  example,
}: {
  page: CurriculumPage;
  example: ExampleBlock;
}) {
  return (
    <section aria-label="Example" data-page-type="example">
      <h1 style={H1} data-component="Heading">
        {page.title}
      </h1>
      {renderContent(page.content)}
      <div style={CARD} data-component="Card" aria-label="What it might look like">
        <p style={CARD_HEADER}>The situation:</p>
        <p style={PARA} data-component="Body">
          {example.situation}
        </p>
        <hr style={DIVIDER} data-component="Divider" />
        <p style={CARD_HEADER}>What Claude might write:</p>
        <p style={CARD_BODY} data-component="Body">
          {example.claude_says}
        </p>
        <hr style={DIVIDER} data-component="Divider" />
        <p style={CARD_HEADER}>The takeaway:</p>
        <p style={{ ...PARA, marginBottom: 0 }} data-component="Body">
          {example.takeaway}
        </p>
      </div>
    </section>
  );
}

export function RetrievalPage({
  page,
  retrieval,
  answered,
}: {
  page: CurriculumPage;
  retrieval: RetrievalBlock;
  /** Null while the learner has not chosen yet; the chosen id once
   *  they pick. The parent controls this state and renders the action
   *  row appropriately (choice buttons vs Continue). */
  answered: string | null;
}) {
  const chosen = answered
    ? retrieval.choices.find((c) => c.id === answered) ?? null
    : null;
  const isCorrect = answered ? answered === retrieval.correct_id : null;

  return (
    <section aria-label="Retrieval" data-page-type="retrieval">
      <h1 style={H1} data-component="Heading">
        {page.title}
      </h1>
      {renderContent(page.content)}
      <p style={{ ...PARA, fontWeight: 600 }} data-component="Body">
        {retrieval.prompt}
      </p>
      {answered && chosen ? (
        <div
          style={isCorrect ? CARD_FEEDBACK_CORRECT : CARD_FEEDBACK_INCORRECT}
          data-component="Card"
          aria-label={isCorrect ? "Correct answer" : "Other answer"}
          role="status"
          aria-live="polite"
        >
          <p style={CARD_HEADER}>
            {isCorrect ? "That fits the rule." : "Take another look."}
          </p>
          <p style={PARA} data-component="Body">
            You chose:{" "}
            <em style={{ fontStyle: "italic" }}>{chosen.text}</em>
          </p>
          <hr style={DIVIDER} data-component="Divider" />
          <p style={CARD_HEADER}>Why:</p>
          <p style={{ ...PARA, marginBottom: 0 }} data-component="Body">
            {retrieval.explanation}
          </p>
        </div>
      ) : null}
    </section>
  );
}

// ---- Proposal builder ------------------------------------------------------
//
// `buildPageProposal` describes the page-body region's contribution to
// the RenderGuard proposal. The parent renderer adds the indicator
// (Indicator component) and the action row's primary-action count
// (NavBar + Continue OR choice buttons) before evaluating the guard.
//
// Color/spacing/radius/motion sets are the UNION of every value any
// sub-renderer might use, so a proposal is valid regardless of which
// page type renders. This is intentional: the guard verifies that the
// proposal's value set is a SUBSET of allowed tokens, and our union is
// already a subset.

export interface PageProposalContribution {
  components: AuthorizedComponent[];
  visibleTextLevels: number;
  /** Additional primary actions contributed by the PAGE BODY (not the
   *  action row, not NavBar). Only retrieval pre-answer adds choice
   *  buttons here; every other page contributes 0. */
  primaryActionsFromBody: number;
}

export function buildPageProposalContribution(
  page: CurriculumPage,
  retrievalAnswered: string | null,
): PageProposalContribution {
  const pageType = page.page_type ?? "principle";
  // Base components present on every page type.
  const components = new Set<AuthorizedComponent>(["Heading", "Body"]);

  if (pageType === "principle" && page.principle) {
    components.add("Card");
  } else if (pageType === "example") {
    components.add("Card");
    components.add("Divider");
  } else if (pageType === "retrieval") {
    // Retrieval choice buttons are page-body primary actions only when
    // the page is in the pre-answer state. Post-answer reveals a Card
    // with feedback and the action row reverts to a single Continue.
    components.add("Button");
    if (retrievalAnswered) {
      components.add("Card");
      components.add("Divider");
    }
  }

  // Visible text levels: every sub-renderer uses h1 (level 1) + body
  // (level 2). The Card "header" lines are body-styled (same scale,
  // weight bump only) so they do not introduce a level 3.
  const visibleTextLevels = 2;

  const primaryActionsFromBody =
    pageType === "retrieval" && retrievalAnswered === null ? 2 : 0;

  return {
    components: Array.from(components),
    visibleTextLevels,
    primaryActionsFromBody,
  };
}

// ---- Token sets used across all sub-renderers ------------------------------
//
// These are the UNION of values referenced by any style object above.
// Exposed so the renderer can pass them into the RenderGuard proposal
// without re-listing them at every call site.

export const PAGE_COLORS_USED: readonly string[] = [
  COLORS.background,
  COLORS.surface,
  COLORS.textPrimary,
  COLORS.accentMutedBlue,
  COLORS.accentDesatGreen,
  COLORS.accentMutedAmber,
  COLORS.disabled,
];

export const PAGE_SPACING_USED: readonly number[] = [
  SPACING.xs,
  SPACING.sm,
  SPACING.md,
  SPACING.lg,
  SPACING.xl,
];

export const PAGE_RADIUS_USED: readonly number[] = [RADIUS.sm, RADIUS.md];

export const PAGE_MOTION_DURATIONS_MS: readonly number[] = [
  MOTION.defaultFadeMs,
];
