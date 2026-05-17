/**
 * Curriculum unit renderer — linear, multi-page-per-unit, contract-bound.
 *
 * Walks a fixed sequence of 15 free-track units (modules 1-3) one at a
 * time. Each unit is now a 1–5 page lesson (Curriculum-expansion
 * Phase 1); Continue advances within the unit's pages, and once the
 * last page is acknowledged advances to the next unit. On the final
 * unit's last page Continue delegates to `onContinueGated` so App.tsx
 * can switch to the paywall view (modules 4-5 are gated behind a
 * one-time purchase).
 *
 * Per ADR 0019 and CONTRACT Section IV:
 *   - Resolves its envelope from `/api/ui-envelope/curriculum.unit`.
 *   - Renders inside a RenderGuard boundary (fail-closed).
 *   - Uses ONLY tokens from `design/tokens.ts`.
 *
 * Page-type dispatch: each page carries an optional `page_type`
 * (recap / context / principle / example / retrieval). Sub-renderers
 * live in `./curriculum/PageTypes.tsx`; the proposal contribution of
 * each is computed by `buildPageProposalContribution` so the
 * RenderGuard math stays adjacent to the JSX.
 *
 * RenderGuard proposal math (verified against `curriculum.unit` envelope
 * after the Phase-1 bump to max_primary_actions=5):
 *
 *   non-retrieval (or retrieval post-answer):
 *     primary actions  = NavBar(≤2) + Continue(1)           = ≤3
 *     highlighted recs = 1 (Continue)                       = max
 *     text levels      = 2 (h1 + body)                      ≤ max(3)
 *
 *   retrieval pre-answer:
 *     primary actions  = NavBar(≤2) + 2 choice Buttons       = ≤4
 *     highlighted recs = 0  (choices are equal options)
 *     text levels      = 2
 *
 * Resume position is persisted to localStorage by ../lib/progress so a
 * learner can close the tab and pick up where they left off, INCLUDING
 * the page index within the unit. Stale or unknown positions fall
 * back to the first unit / first page.
 */
import { CSSProperties, useEffect, useMemo, useRef, useState } from "react";
import {
  loadFreeLesson,
  recordRetrievalChoice,
  type CurriculumPage,
  type LessonResponse,
} from "../api/curriculum";
import { loadEnvelope } from "../api/envelope";
import {
  readProgress,
  writeProgress,
  type Progress,
} from "../lib/progress";
import {
  COLORS,
  SPACING,
  TYPOGRAPHY,
  RADIUS,
  MOTION,
} from "../design/tokens";
import type { UIStateEnvelope } from "../design/envelope";
import { RenderGuard, type RenderProposal } from "../design/RenderGuard";
import NavBar from "./NavBar";
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
} from "./curriculum/PageTypes";

interface Props {
  onSignIn?: () => void;
  /** S25.1: open the lesson menu / table of contents. Wired from
   *  App.tsx; surfaces in NavBar as a "Lessons" entry. */
  onOpenMenu?: () => void;
  /** Invoked when Continue is pressed on the final free unit. App.tsx
   *  routes this to setView("paywall"). The same handler is wired to
   *  NavBar's Upgrade button so the navigation target is consistent
   *  whether the user clicks Continue or the nav entry. */
  onContinueGated: () => void;
  onAccount?: () => void;
}

// Free-track entries narrow `module` from Progress's 1..5 to 1..3 so the
// loadFreeUnit call site type-checks without a runtime cast.
type FreeProgress = Omit<Progress, "module"> & { module: 1 | 2 | 3 };

// Canonical free-track order. IDs verified at design time against
// backend/models/curriculum_units*.py. Sprint 24 promoted unit-1 to
// the head of the sequence as the "Meet Claude" foundation lesson:
// the AI → Claude → Anthropic conceptual bridge that unit-2 was
// implicitly assuming.
const FREE_SEQUENCE: ReadonlyArray<FreeProgress> = [
  { module: 1, unitId: "unit-1" },
  { module: 1, unitId: "unit-2" },
  { module: 1, unitId: "unit-3" },
  { module: 1, unitId: "unit-4" },
  { module: 1, unitId: "unit-5" },
  { module: 1, unitId: "unit-6" },
  { module: 1, unitId: "unit-7" },
  { module: 2, unitId: "module2-unit-1" },
  { module: 2, unitId: "module2-unit-2" },
  { module: 2, unitId: "module2-unit-3" },
  { module: 2, unitId: "module2-unit-4" },
  { module: 2, unitId: "module2-unit-5" },
  { module: 3, unitId: "module3-unit-1" },
  { module: 3, unitId: "module3-unit-2" },
  { module: 3, unitId: "module3-unit-3" },
  { module: 3, unitId: "module3-unit-4" },
];

// ---- Tokenized style objects ------------------------------------------------

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

// S23.2 Previous button: reversible navigation, non-highlighted so it does
// not compete with the single primary recommendation (Continue). Per
// CONTRACT §I.F the primary-action ceiling stays ≤5 — worst case here is
// NavBar(2) + Continue(1) + Previous(1) = 4. Reversible by definition so
// it cannot be the irreversible action.
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

// ---- Loading / blocked sub-renderers ---------------------------------------

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

// ---- Page-body dispatch ----------------------------------------------------

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
  // Default = principle (also covers legacy pages with no page_type).
  return <PrinciplePage page={page} />;
}

// ---- Component --------------------------------------------------------------

export default function CurriculumRenderer({
  onSignIn,
  onOpenMenu,
  onContinueGated,
  onAccount,
}: Props) {
  // Resume from localStorage; fall back to first unit / first page if
  // missing or stale. `pageIdx` is clamped to the unit's lesson length
  // once the lesson is loaded.
  const initialPosition = useMemo(() => {
    const saved = readProgress();
    if (!saved) return { idx: 0, pageIdx: 0 };
    const i = FREE_SEQUENCE.findIndex(
      (p) => p.module === saved.module && p.unitId === saved.unitId,
    );
    return {
      idx: i >= 0 ? i : 0,
      pageIdx: i >= 0 ? saved.pageIdx ?? 0 : 0,
    };
  }, []);

  const [idx, setIdx] = useState(initialPosition.idx);
  const [pageIdx, setPageIdx] = useState(initialPosition.pageIdx);
  const [lesson, setLesson] = useState<LessonResponse | null>(null);
  const [envelope, setEnvelope] = useState<UIStateEnvelope | null>(null);
  const [error, setError] = useState<string | null>(null);
  /** Null until the learner picks a retrieval choice on the current
   *  page, then the chosen choice id. Reset on every page change. */
  const [retrievalAnswered, setRetrievalAnswered] = useState<string | null>(
    null,
  );
  // S23.2: one-shot flag set by handlePrevious when reversing across a
  // unit boundary. Held in a ref (not state) so it does not appear in
  // the lesson-load effect's dependency array — if it did, toggling it
  // would re-trigger the fetch. The flag is consumed (read + reset)
  // exactly once when the previous unit's lesson resolves.
  const pendingBackNavRef = useRef(false);

  // Envelope: load once. Cancelled flag covers React 18 StrictMode
  // double-invoke in development.
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

  // Lesson content: refetch on every idx change. Stale responses
  // dropped by the cancelled flag so rapid Continue presses don't race.
  useEffect(() => {
    let cancelled = false;
    setLesson(null);
    setError(null);
    setRetrievalAnswered(null);
    const { module, unitId } = FREE_SEQUENCE[idx];
    loadFreeLesson(module, unitId)
      .then((l) => {
        if (cancelled) return;
        setLesson(l);
        // S23.2: cross-unit Previous lands us on the previous unit's
        // LAST page. We read-and-clear the ref here so the flag is
        // consumed exactly once per back-nav.
        const wasBackNav = pendingBackNavRef.current;
        pendingBackNavRef.current = false;
        // Clamp pageIdx to the loaded lesson; persisted values from a
        // previous deploy can legitimately point past the new end.
        setPageIdx((current) => {
          let safe: number;
          if (wasBackNav) {
            safe = l.pages.length - 1;
          } else if (current < 0 || current >= l.pages.length) {
            safe = 0;
          } else {
            safe = current;
          }
          writeProgress({ module, unitId, pageIdx: safe });
          return safe;
        });
      })
      .catch((e: unknown) => {
        if (cancelled) return;
        setError(e instanceof Error ? e.message : "Failed to load lesson");
      });
    return () => {
      cancelled = true;
    };
  }, [idx]);

  // Re-persist on every successful page change within the unit.
  useEffect(() => {
    if (!lesson) return;
    const { module, unitId } = FREE_SEQUENCE[idx];
    writeProgress({ module, unitId, pageIdx });
    setRetrievalAnswered(null);
  }, [pageIdx, idx, lesson]);

  const handleContinue = () => {
    if (!lesson) return;
    // Advance within the current unit's pages first.
    if (pageIdx < lesson.pages.length - 1) {
      setPageIdx((p) => p + 1);
      return;
    }
    // End of unit: advance to next unit, reset to its first page.
    if (idx >= FREE_SEQUENCE.length - 1) {
      onContinueGated();
      return;
    }
    setPageIdx(0);
    setIdx((i) => i + 1);
  };

  // S23.2: reversible counterpart to handleContinue. Walks back through
  // the current unit's pages, then across to the previous unit's last
  // page once pageIdx hits 0. At idx=0 + pageIdx=0 the button is not
  // rendered (canGoPrevious=false), so this handler is unreachable.
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
    const { module, unitId } = FREE_SEQUENCE[idx];
    void recordRetrievalChoice({
      module,
      unit_id: unitId,
      page_id: page.id,
      chosen_id: chosenId,
      correct: chosenId === page.retrieval.correct_id,
    });
  };

  const nav = (
    <NavBar
      onSignIn={onSignIn}
      onContinuePaid={onContinueGated}
      onAccount={onAccount}
      onOpenMenu={onOpenMenu}
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
  const { module } = FREE_SEQUENCE[idx];
  const isLastUnit = idx >= FREE_SEQUENCE.length - 1;
  const isLastPage = pageIdx >= lesson.pages.length - 1;
  const isRetrievalPage =
    (page.page_type ?? "principle") === "retrieval" && !!page.retrieval;
  const showChoices = isRetrievalPage && retrievalAnswered === null;
  const showContinue = !showChoices;
  // Previous button shares the showContinue gate — during retrieval
  // pre-answer (the only state without Continue) the choice buttons are
  // the sole primary actions. The learner regains Previous after picking,
  // or can use the NavBar to leave the lesson entirely.
  const canGoPrevious = (idx > 0 || pageIdx > 0) && showContinue;
  const continueLabel =
    isLastUnit && isLastPage ? "Continue to paid modules →" : "Continue →";

  // ---- Proposal accounting -------------------------------------------------
  //
  // NavBar contribution: up to 3 primary actions when signed in with
  // the menu enabled (Upgrade + Account + Lessons). We use the worst
  // case so the proposal is valid regardless of session state.
  // Pre-answer retrieval: 3 NavBar + 2 choice Buttons = 5 (envelope ceiling).
  // Other pages:           3 NavBar + Continue + Previous = 5 (also ceiling).
  const NAVBAR_PRIMARY_ACTIONS = onOpenMenu ? 3 : 2;
  const contribution = buildPageProposalContribution(
    page,
    retrievalAnswered,
  );

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

  // Continue is the single highlighted recommendation. Choice buttons
  // are equal options, never highlighted.
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
          Module {module} · Lesson {idx + 1} of {FREE_SEQUENCE.length} ·
          Page {pageIdx + 1} of {lesson.pages.length}
        </p>
        {renderPageBody(page, retrievalAnswered)}
        {showChoices && page.retrieval ? (
          <div
            style={CHOICES_COLUMN}
            role="group"
            aria-label="Pick one"
          >
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
              // Empty span keeps the flex space-between layout stable
              // so Continue stays right-aligned on the first page.
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
