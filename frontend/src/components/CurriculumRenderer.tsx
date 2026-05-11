/**
 * Curriculum unit renderer — contract-bound.
 *
 * Per ADR 0019 and CONTRACT Section IV:
 *   - Resolves its envelope from `/api/ui-envelope/curriculum.unit`.
 *   - Renders inside a RenderGuard boundary (fail-closed).
 *   - Uses ONLY tokens from `design/tokens.ts`.
 *
 * The unit's content (title + lines) still comes from the ISCS-approved
 * `loadWhatIsAI` endpoint; this component does NOT derive UI complexity.
 */
import { CSSProperties, useEffect, useState } from "react";
import { loadWhatIsAI, ApprovedUIState } from "../api/interfaceController";
import { loadEnvelope } from "../api/envelope";
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
  onReturn?: () => void;
  onSignIn?: () => void;
  onContinuePaid?: () => void;
  onAccount?: () => void;
}

// ---- Tokenized style objects ------------------------------------------------

const PAGE: CSSProperties = {
  padding: SPACING.xl,
  maxWidth: 680,
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

const RETURN_BTN: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.sm}px ${SPACING.md}px`,
  backgroundColor: COLORS.surface,
  color: COLORS.accentMutedBlue,
  border: `1px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.sm,
  cursor: "pointer",
  transition: `opacity ${MOTION.defaultFadeMs}ms ease-out`,
};

const NAV: CSSProperties = {
  marginBottom: SPACING.lg,
};

const PARA: CSSProperties = {
  marginTop: 0,
  marginBottom: SPACING.md,
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
  onReturn,
  onSignIn,
  onContinuePaid,
  onAccount,
}: Props) {
  const [unit, setUnit] = useState<ApprovedUIState | null>(null);
  const [envelope, setEnvelope] = useState<UIStateEnvelope | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([loadEnvelope("curriculum.unit"), loadWhatIsAI()])
      .then(([env, approved]) => {
        setEnvelope(env);
        setUnit(approved);
      })
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : "Failed to load"),
      );
  }, []);

  const nav = (
    <>
      <NavBar
        onSignIn={onSignIn}
        onContinuePaid={onContinuePaid}
        onAccount={onAccount}
      />
      {onReturn ? (
        <nav aria-label="Lesson navigation" style={NAV}>
          <button type="button" onClick={onReturn} style={RETURN_BTN}>
            Return to start
          </button>
        </nav>
      ) : null}
    </>
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

  // Proposal: what this render intends to display.
  // NavBar always contributes a Button slot; return-to-start adds another.
  const proposal: RenderProposal = {
    components: ["Heading", "Body", "Button"],
    // return-to-start + up to 2 NavBar entries.
    primaryActionCount: (onReturn ? 1 : 0) + 2,
    irreversibleActionCount: 0,
    highlightedRecommendationCount: 0,
    visibleTextLevels: 2, // h1, body
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
      </main>
    </RenderGuard>
  );
}
