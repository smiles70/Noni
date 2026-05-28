/**
 * LessonRenderer — the shared core for linear, multi-page-per-unit,
 * contract-bound curriculum rendering.
 *
 * Extracted from CurriculumRenderer in Sprint "paid modules" P4 so
 * both the free track (M1–M3) and the paid bundle (M4–M5) can reuse the
 * same NavBar, Indicator, Previous/Continue flow, retrieval handling,
 * progress persistence, and RenderGuard accounting without duplication.
 *
 * This component is track-agnostic: it receives an ordered sequence of
 * unit references and a loader function, then walks the learner through
 * them exactly as CurriculumRenderer did before extraction.
 *
 * Per ADR 0019 and CONTRACT Section IV:
 *   - Resolves its envelope from `/api/ui-envelope/curriculum.unit`.
 *   - Renders inside a RenderGuard boundary (fail-closed).
 *   - Uses ONLY tokens from `design/tokens.ts`.
 *
 * Page-type dispatch: each page carries an optional `page_type`
 * (recap / context / principle / example / retrieval). Sub-renderers
 * live in `./PageTypes.tsx`; the proposal contribution of each is
 * computed by `buildPageProposalContribution` so the RenderGuard math
 * stays adjacent to the JSX.
 */

import { CSSProperties, useEffect, useRef, useState } from "react";
import {
  recordRetrievalChoice,
  PaywallError,
  type CurriculumPage,
  type LessonResponse,
  type PaywallSignal,
} from "../../api/curriculum";
import { loadEnvelope } from "../../api/envelope";
import {
  readProgress,
  writeProgress,
} from "../../lib/progress";
import {
  COLORS,
  SPACING,
  TYPOGRAPHY,
  RADIUS,
  MOTION,
} from "../../design/tokens";
import type { UIStateEnvelope } from "../../design/envelope";
import { RenderGuard, type RenderProposal } from "../../design/RenderGuard";
import NavBar from "../NavBar";
import {
  RecapPage,
  ContextPage,
  PrinciplePage,
  ExamplePage,
  RetrievalPage,
  buildPageProposalContribution,
  PAGE_COLORS_USED,
  PAGE_SPACING_USED,
  PAGE_RADIUS_USED,
  PAGE_MOTION_DURATIONS_MS,
} from "./PageTypes";

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface LessonRendererProps {
  /** Ordered list of units to walk. Each entry carries the module
   *  number and the backend unit id. */
  sequence: ReadonlyArray<{ module: number; unitId: string }>;
  /** Loader for a single unit's lesson. Must return a `LessonResponse`
   *  with `pages` in author order. */
  loadLesson: (module: number, unitId: string) => Promise<LessonResponse>;
  /** Called when the learner presses Continue on the last page of the
   *  final unit in the sequence. The parent routes this (e.g. to the
   *  paywall or to a celebration screen). */
  onSequenceComplete: () => void;
  onSignIn?: () => void;
  onOpenMenu?: () => void;
  onAccount?: () => void;
  /** NavBar "Upgrade" button. Only provided by the free track; the
   *  paid track omits it so the learner does not see an Upgrade button
   *  while already inside paid content. */
  onContinuePaid?: () => void;
  /** Called when a paid lesson load returns 402. The parent should
   *  switch to the paywall view. Only used by the paid track. */
  onPaywall?: (signal: PaywallSignal) => void;
  /** Optional Continue-button label override. Default matches the
   *  pre-extraction free-track behaviour. */
  getContinueLabel?: (isLastUnit: boolean, isLastPage: boolean) => string;
  onHelp?: () => void;
}

// ---------------------------------------------------------------------------
// Styles (unchanged from pre-extraction CurriculumRenderer)
// ---------------------------------------------------------------------------

const PAGE: CSSProperties = {
  padding: SPACING.xl,
  maxWidth: 720,
  margin: "0 auto",
  fontSize: TYPOGRAPHY.bodySizePx,
  lineHeight: TYPOGRAPHY.bodyLineHeight,
  fontFamily: TYPOGRAPHY.fontFamily,
  color: COLORS.textPrimary,
  backgroundColor: COLORS.background,
};

const H1: CSSProperties = {
  fontSize: TYPOGRAPHY.headingScale.level1,
  marginTop: 0,
  marginBottom: SPACING.md,
  color: COLORS.textPrimary,
};

const PARA: CSSProperties = {
  marginTop: 0,
  marginBottom: SPACING.md,
};

const INDICATOR: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  color: COLORS.textPrimary,
  opacity: 0.7,
  marginTop: 0,
  marginBottom: SPACING.md,
};

const ACTIONS: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginTop: SPACING.lg,
  gap: SPACING.sm,
};

const CONTINUE_BTN: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.md}px ${SPACING.lg}px`,
  backgroundColor: COLORS.accentMutedBlue,
  color: COLORS.surface,
  border: `2px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.sm,
  fontWeight: 600,
  cursor: "pointer",
  transition: `opacity ${MOTION.defaultFadeMs}ms ease-out`,
};

const PREVIOUS_BTN: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.sm}px ${SPACING.md}px`,
  backgroundColor: COLORS.surface,
  color: COLORS.textPrimary,
  border: `1px solid ${COLORS.disabled}`,
  borderRadius: RADIUS.sm,
  fontWeight: 500,
  cursor: "pointer",
  transition: `opacity ${MOTION.defaultFadeMs}ms ease-out`,
  fontFamily: TYPOGRAPHY.fontFamily,
};

const ERROR_DETAIL: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  marginTop: SPACING.sm,
  color: COLORS.textPrimary,
};

const CHOICE_BTN: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.md}px ${SPACING.lg}px`,
  backgroundColor: COLORS.surface,
  color: COLORS.textPrimary,
  border: `2px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.sm,
  fontWeight: 600,
  cursor: "pointer",
  transition: `opacity ${MOTION.defaultFadeMs}ms ease-out`,
  textAlign: "left",
  fontFamily: TYPOGRAPHY.fontFamily,
  lineHeight: TYPOGRAPHY.bodyLineHeight,
};

const CHOICES_COLUMN: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: SPACING.sm,
  marginTop: SPACING.lg,
};

// ---------------------------------------------------------------------------
// Sub-renderers
// ---------------------------------------------------------------------------

function PendingBanner({ nav }: { nav: React.ReactNode }) {
  return (
    <main style={PAGE} aria-live="polite" data-component="PendingBanner">
      {nav}
      <p style={PARA}>One moment — loading.</p>
    </main>
  );
}

function BlockedLoad({
  message,
  detail,
  nav,
}: {
  message: string;
  detail?: string;
  nav: React.ReactNode;
}) {
  return (
    <main
      style={{ ...PAGE, borderRadius: RADIUS.md }}
      role="alert"
      aria-live="polite"
      data-component="BlockedNotice"
    >
      {nav}
      <h1 style={H1}>This lesson is paused.</h1>
      <p style={PARA}>{message}</p>
      {detail ? <p style={ERROR_DETAIL}>{detail}</p> : null}
    </main>
  );
}

function renderPageBody(
  page: CurriculumPage,
  retrievalAnswered: string | null,
): React.ReactElement {
  const pageType = page.page_type ?? "principle";
  if (pageType === "recap") return <RecapPage page={page} />;
  if (pageType === "context") return <ContextPage page={page} />;
  if (pageType === "example" && page.example) {
    return <ExamplePage page={page} example={page.example} />;
  }
  if (pageType === "retrieval" && page.retrieval) {
    return (
      <RetrievalPage
        page={page}
        retrieval={page.retrieval}
        answered={retrievalAnswered}
      />
    );
  }
  return <PrinciplePage page={page} />;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function LessonRenderer({
  sequence,
  loadLesson,
  onSequenceComplete,
  onSignIn,
  onOpenMenu,
  onAccount,
  onContinuePaid,
  onPaywall,
  onHelp,
  getContinueLabel = (isLastUnit, isLastPage) =>
    isLastUnit && isLastPage
      ? "Continue to paid modules →"
      : "Continue →",
}: LessonRendererProps) {
  // Resume from localStorage; fall back to first unit / first page if
  // missing or stale. `pageIdx` is clamped to the unit's lesson length
  // once the lesson is loaded.
  const initialPosition = (() => {
    const saved = readProgress();
    if (!saved) return { idx: 0, pageIdx: 0 };
    const i = sequence.findIndex(
      (p) => p.module === saved.module && p.unitId === saved.unitId,
    );
    return {
      idx: i >= 0 ? i : 0,
      pageIdx: i >= 0 ? saved.pageIdx ?? 0 : 0,
    };
  })();

  const [idx, setIdx] = useState(initialPosition.idx);
  const [pageIdx, setPageIdx] = useState(initialPosition.pageIdx);
  const [lesson, setLesson] = useState<LessonResponse | null>(null);
  const [envelope, setEnvelope] = useState<UIStateEnvelope | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [retrievalAnswered, setRetrievalAnswered] = useState<string | null>(
    null,
  );
  const pendingBackNavRef = useRef(false);

  // Envelope: load once.
  useEffect(() => {
    let cancelled = false;
    loadEnvelope("curriculum.unit")
      .then((env) => {
        if (!cancelled) setEnvelope(env);
      })
      .catch((e: unknown) => {
        if (!cancelled) {
          setError(
            e instanceof Error ? e.message : "Failed to load envelope",
          );
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // Lesson content: refetch on every idx change.
  useEffect(() => {
    let cancelled = false;
    setLesson(null);
    setError(null);
    setRetrievalAnswered(null);
    const { module, unitId } = sequence[idx];
    loadLesson(module, unitId)
      .then((l) => {
        if (cancelled) return;
        setLesson(l);
        const wasBackNav = pendingBackNavRef.current;
        pendingBackNavRef.current = false;
        setPageIdx((current) => {
          let safe: number;
          if (wasBackNav) {
            safe = l.pages.length - 1;
          } else if (current < 0 || current >= l.pages.length) {
            safe = 0;
          } else {
            safe = current;
          }
          writeProgress({ module: module as 0 | 1 | 2 | 3 | 4 | 5, unitId, pageIdx: safe });
          return safe;
        });
      })
      .catch((e: unknown) => {
        if (cancelled) return;
        if (e instanceof PaywallError && onPaywall) {
          onPaywall(e.signal);
          return;
        }
        setError(e instanceof Error ? e.message : "Failed to load lesson");
      });
    return () => {
      cancelled = true;
    };
  }, [idx]);

  // Re-persist on every successful page change within the unit.
  useEffect(() => {
    if (!lesson) return;
    const { unitId } = sequence[idx];
    writeProgress({ module: sequence[idx].module as 0 | 1 | 2 | 3 | 4 | 5, unitId, pageIdx });
    setRetrievalAnswered(null);
  }, [pageIdx, idx, lesson]);

  const handleContinue = () => {
    if (!lesson) return;
    if (pageIdx < lesson.pages.length - 1) {
      setPageIdx((p) => p + 1);
      return;
    }
    if (idx >= sequence.length - 1) {
      onSequenceComplete();
      return;
    }
    setPageIdx(0);
    setIdx((i) => i + 1);
  };

  const handlePrevious = () => {
    if (!lesson) return;
    if (pageIdx > 0) {
      setPageIdx((p) => p - 1);
      return;
    }
    if (idx > 0) {
      pendingBackNavRef.current = true;
      setIdx((i) => i - 1);
    }
  };

  const handleChoice = (chosenId: string) => {
    if (!lesson) return;
    const page = lesson.pages[pageIdx];
    if (!page.retrieval) return;
    setRetrievalAnswered(chosenId);
    const { module, unitId } = sequence[idx];
    void recordRetrievalChoice({
      module: module as 0 | 1 | 2 | 3 | 4 | 5,
      unit_id: unitId,
      page_id: page.id,
      chosen_id: chosenId,
      correct: chosenId === page.retrieval.correct_id,
    });
  };

  const nav = (
    <NavBar
      onSignIn={onSignIn}
      onContinuePaid={onContinuePaid}
      onAccount={onAccount}
      onOpenMenu={onOpenMenu}
      onHelp={onHelp}
    />
  );

  if (error) {
    return (
      <BlockedLoad
        message="We are having trouble reaching the lesson. You can try again in a moment."
        detail={error}
        nav={nav}
      />
    );
  }

  if (!lesson || !envelope) {
    return <PendingBanner nav={nav} />;
  }

  const page = lesson.pages[pageIdx] ?? lesson.pages[0];
  const { module } = sequence[idx];
  const isLastUnit = idx >= sequence.length - 1;
  const isLastPage = pageIdx >= lesson.pages.length - 1;
  const isRetrievalPage =
    (page.page_type ?? "principle") === "retrieval" && !!page.retrieval;
  const showChoices = isRetrievalPage && retrievalAnswered === null;
  const showContinue = !showChoices;
  const canGoPrevious = (idx > 0 || pageIdx > 0) && showContinue;
  const continueLabel = getContinueLabel(isLastUnit, isLastPage);

  // ---- Proposal accounting ----
  const NAVBAR_PRIMARY_ACTIONS = onOpenMenu ? 3 : 2;
  const contribution = buildPageProposalContribution(page, retrievalAnswered);

  const components = new Set<RenderProposal["components"][number]>(
    contribution.components,
  );
  components.add("Indicator");
  if (showContinue) components.add("Button");
  if (showChoices) components.add("Button");

  const primaryActionCount =
    NAVBAR_PRIMARY_ACTIONS +
    (showContinue ? 1 : 0) +
    (canGoPrevious ? 1 : 0) +
    contribution.primaryActionsFromBody;

  const highlightedRecommendationCount = showContinue ? 1 : 0;

  const proposal: RenderProposal = {
    components: Array.from(components),
    primaryActionCount,
    irreversibleActionCount: 0,
    highlightedRecommendationCount,
    visibleTextLevels: contribution.visibleTextLevels,
    colorsUsed: [...PAGE_COLORS_USED],
    spacingPxUsed: [...PAGE_SPACING_USED],
    radiusPxUsed: [...PAGE_RADIUS_USED],
    motionDurationsMs: [...PAGE_MOTION_DURATIONS_MS],
    positionShiftPxUsed: [],
    hasUnconfirmedIrreversibleAction: false,
    usesOptimisticProgression: false,
  };

  return (
    <RenderGuard envelope={envelope} proposal={proposal}>
      <main style={PAGE}>
        {nav}
        <p style={INDICATOR} data-component="Indicator">
          Module {module} · Lesson {idx + 1} of {sequence.length} · Page{" "}
          {pageIdx + 1} of {lesson.pages.length}
        </p>
        {renderPageBody(page, retrievalAnswered)}
        {showChoices && page.retrieval ? (
          <div style={CHOICES_COLUMN} role="group" aria-label="Pick one">
            {page.retrieval.choices.map((c) => (
              <button
                key={c.id}
                type="button"
                onClick={() => handleChoice(c.id)}
                style={CHOICE_BTN}
                data-component="Button"
                data-choice-id={c.id}
              >
                {c.text}
              </button>
            ))}
          </div>
        ) : null}
        {showContinue ? (
          <div style={ACTIONS}>
            {canGoPrevious ? (
              <button
                type="button"
                onClick={handlePrevious}
                style={PREVIOUS_BTN}
                aria-label="Go to previous page"
                data-component="Button"
              >
                ← Previous
              </button>
            ) : (
              <span />
            )}
            <button
              type="button"
              onClick={handleContinue}
              style={CONTINUE_BTN}
              aria-label={continueLabel}
              data-component="Button"
            >
              {continueLabel}
            </button>
          </div>
        ) : null}
      </main>
    </RenderGuard>
  );
}
