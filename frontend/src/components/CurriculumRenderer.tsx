/**
 * Curriculum unit renderer — linear, contract-bound.
 *
 * Walks a fixed sequence of 15 free-track units (modules 1-3) one at a
 * time. Continue advances within the sequence; on the final entry it
 * delegates to `onContinueGated` so App.tsx can switch to the paywall
 * view (modules 4-5 are gated behind a one-time purchase).
 *
 * Per ADR 0019 and CONTRACT Section IV:
 *   - Resolves its envelope from `/api/ui-envelope/curriculum.unit`.
 *   - Renders inside a RenderGuard boundary (fail-closed).
 *   - Uses ONLY tokens from `design/tokens.ts`.
 *
 * RenderGuard proposal math (verified against `curriculum.unit` envelope):
 *   primary actions    = NavBar(2 signed-in) + Continue(1) = 3 = max
 *   highlighted recs   = 1 (Continue) = max
 *   visibleTextLevels  = 2 (h1 + body) <= max(3)
 *   components in {Heading, Body, Button, Indicator} ⊂ authorized set
 *
 * Resume position is persisted to localStorage by ../lib/progress so a
 * learner can close the tab and pick up where they left off. Stale or
 * unknown positions fall back to the first unit.
 */
import { CSSProperties, useEffect, useMemo, useState } from "react";
import { loadFreeUnit, type ApprovedUnit } from "../api/curriculum";
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

interface Props {
  onSignIn?: () => void;
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
// backend/models/curriculum_units*.py (module 1 reserves unit-1 / does
// not expose it; the real sequence starts at unit-2).
const FREE_SEQUENCE: ReadonlyArray<FreeProgress> = [
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
  justifyContent: "flex-end",
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

// ---- Component --------------------------------------------------------------

export default function CurriculumRenderer({
  onSignIn,
  onContinueGated,
  onAccount,
}: Props) {
  // Resume from localStorage; fall back to first unit if missing/stale.
  const initialIdx = useMemo(() => {
    const saved = readProgress();
    if (!saved) return 0;
    const i = FREE_SEQUENCE.findIndex(
      (p) => p.module === saved.module && p.unitId === saved.unitId,
    );
    return i >= 0 ? i : 0;
  }, []);

  const [idx, setIdx] = useState(initialIdx);
  const [unit, setUnit] = useState<ApprovedUnit | null>(null);
  const [envelope, setEnvelope] = useState<UIStateEnvelope | null>(null);
  const [error, setError] = useState<string | null>(null);

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

  // Unit content: refetch on every idx change. Stale responses dropped
  // by the cancelled flag so rapid Continue presses don't race.
  useEffect(() => {
    let cancelled = false;
    setUnit(null);
    setError(null);
    const { module, unitId } = FREE_SEQUENCE[idx];
    loadFreeUnit(module, unitId)
      .then((u) => {
        if (cancelled) return;
        setUnit(u);
        writeProgress({ module, unitId });
      })
      .catch((e: unknown) => {
        if (cancelled) return;
        setError(e instanceof Error ? e.message : "Failed to load unit");
      });
    return () => {
      cancelled = true;
    };
  }, [idx]);

  const handleContinue = () => {
    if (idx >= FREE_SEQUENCE.length - 1) {
      onContinueGated();
      return;
    }
    setIdx((i) => i + 1);
  };

  const nav = (
    <NavBar
      onSignIn={onSignIn}
      onContinuePaid={onContinueGated}
      onAccount={onAccount}
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

  if (!unit || !envelope) {
    return <PendingBanner nav={nav} />;
  }

  const page = unit.ui_state;
  const { module } = FREE_SEQUENCE[idx];
  const isLast = idx >= FREE_SEQUENCE.length - 1;
  const continueLabel = isLast
    ? "Continue to paid modules →"
    : "Continue →";

  // RenderGuard proposal — math verified against curriculum.unit envelope:
  //   primary actions     = NavBar(2 signed-in) + Continue(1) = 3 = max
  //   highlighted recs    = 1 (Continue)                          = max
  //   visibleTextLevels   = 2 (h1 + body; Indicator is body-styled) <= max(3)
  //   components          ⊂ {Heading, Body, Button, Card, Divider,
  //                          Indicator, PendingBanner, BlockedNotice}
  const proposal: RenderProposal = {
    components: ["Heading", "Body", "Button", "Indicator"],
    primaryActionCount: 3,
    irreversibleActionCount: 0,
    highlightedRecommendationCount: 1,
    visibleTextLevels: 2,
    colorsUsed: [
      COLORS.background,
      COLORS.surface,
      COLORS.textPrimary,
      COLORS.accentMutedBlue,
    ],
    spacingPxUsed: [SPACING.xs, SPACING.sm, SPACING.md, SPACING.lg, SPACING.xl],
    radiusPxUsed: [RADIUS.sm],
    motionDurationsMs: [MOTION.defaultFadeMs],
    positionShiftPxUsed: [],
    hasUnconfirmedIrreversibleAction: false,
    usesOptimisticProgression: false,
  };

  return (
    <RenderGuard envelope={envelope} proposal={proposal}>
      <main style={PAGE}>
        {nav}
        <p style={INDICATOR} data-component="Indicator">
          Module {module} · Lesson {idx + 1} of {FREE_SEQUENCE.length}
        </p>
        <header>
          <h1 style={H1}>{page.title}</h1>
        </header>
        <section aria-label="Lesson content">
          {page.content.map((line, i) => (
            <p key={i} style={PARA}>
              {line}
            </p>
          ))}
        </section>
        <div style={ACTIONS}>
          <button
            type="button"
            onClick={handleContinue}
            style={CONTINUE_BTN}
            aria-label={continueLabel}
          >
            {continueLabel}
          </button>
        </div>
      </main>
    </RenderGuard>
  );
}
