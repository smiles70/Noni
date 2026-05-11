/**
 * Landing page — contract-bound renderer.
 *
 * Per ADR 0019 and CONTRACT Section IV, this component:
 *   - Resolves its envelope from `/api/ui-envelope/landing.page` on mount.
 *   - Renders inside a RenderGuard boundary that fails closed on any
 *     contract violation.
 *   - Uses ONLY tokens from `design/tokens.ts` for color, spacing, type,
 *     radius, and motion. No raw hex literals, no arbitrary spacing values.
 *
 * Copy still comes from the backend (`/api/landing/page`, per ADR 0006).
 */
import { CSSProperties, useEffect, useState } from "react";
import { loadLandingPage, LandingPageContent } from "../api/landing";
import { loadEnvelope } from "../api/envelope";
import { isLargeText, toggleLargeText } from "../largeText";
import {
  COLORS,
  SPACING,
  TYPOGRAPHY,
  RADIUS,
  FOCUS,
  MOTION,
} from "../design/tokens";
import type { UIStateEnvelope } from "../design/envelope";
import { RenderGuard, type RenderProposal } from "../design/RenderGuard";
import NavBar from "./NavBar";

interface Props {
  onBegin: () => void;
  onSignIn?: () => void;
  onContinuePaid?: () => void;
  onAccount?: () => void;
}

// ---- Tokenized style objects -----------------------------------------------

const PAGE: CSSProperties = {
  padding: SPACING.xl,
  maxWidth: 680, // 85 × 8px = grid-aligned
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
  marginBottom: SPACING.sm,
  color: COLORS.textPrimary,
};

const H2: CSSProperties = {
  fontSize: TYPOGRAPHY.headingScale.level2,
  marginTop: 0,
  marginBottom: SPACING.md,
  color: COLORS.textPrimary,
};

const SUBHEAD: CSSProperties = {
  fontSize: TYPOGRAPHY.headingScale.level3,
  color: COLORS.textPrimary,
  marginTop: 0,
};

const PRIMARY_BTN: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.md}px ${SPACING.lg}px`,
  backgroundColor: COLORS.accentMutedBlue,
  color: COLORS.surface, // WCAG-AA contrast against muted blue
  border: `2px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.sm,
  fontWeight: 600,
  cursor: "pointer",
  transition: `opacity ${MOTION.defaultFadeMs}ms ease-out`,
};

const SECONDARY_BTN: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.md}px ${SPACING.lg}px`,
  backgroundColor: COLORS.surface,
  color: COLORS.accentMutedBlue,
  border: `2px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.sm,
  fontWeight: 600,
  cursor: "pointer",
  transition: `opacity ${MOTION.defaultFadeMs}ms ease-out`,
};

const TEXT_TOGGLE: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.sm}px ${SPACING.md}px`,
  backgroundColor: COLORS.surface,
  color: COLORS.accentMutedBlue,
  border: `1px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.sm,
  cursor: "pointer",
  transition: `opacity ${MOTION.defaultFadeMs}ms ease-out`,
};

const CTA_NOTE: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  color: COLORS.textPrimary,
  marginTop: SPACING.sm,
};

const SECTION: CSSProperties = {
  marginTop: SPACING.xl,
};

const DIVIDER: CSSProperties = {
  border: 0,
  borderTop: `1px solid ${COLORS.disabled}`,
  margin: `${SPACING.xl}px 0`,
};

const CTA_GROUP: CSSProperties = {
  marginTop: SPACING.xxl,
  display: "flex",
  flexDirection: "column",
  gap: SPACING.lg,
};

// ---- Loading / blocked states ----------------------------------------------

function PendingBanner() {
  return (
    <main
      style={PAGE}
      aria-live="polite"
      data-component="PendingBanner"
    >
      <p style={{ margin: 0 }}>One moment — loading.</p>
    </main>
  );
}

function BlockedLoad({ message }: { message: string }) {
  return (
    <main
      style={{ ...PAGE, borderRadius: RADIUS.md }}
      role="alert"
      aria-live="polite"
      data-component="BlockedNotice"
    >
      <h1 style={H1}>This page is paused.</h1>
      <p>{message}</p>
    </main>
  );
}

// ---- Component -------------------------------------------------------------

function paragraphs(text: string) {
  return text.split("\n\n").map((p, i) => (
    <p key={i} style={{ marginTop: 0, marginBottom: SPACING.md }}>
      {p}
    </p>
  ));
}

export default function LandingPage({
  onBegin,
  onSignIn,
  onContinuePaid,
  onAccount,
}: Props) {
  const [content, setContent] = useState<LandingPageContent | null>(null);
  const [envelope, setEnvelope] = useState<UIStateEnvelope | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [largeText, setLargeText] = useState<boolean>(isLargeText());

  useEffect(() => {
    Promise.all([loadEnvelope("landing.page"), loadLandingPage()])
      .then(([env, page]) => {
        setEnvelope(env);
        setContent(page);
      })
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : "Failed to load"),
      );
  }, []);

  const handleToggleText = () => setLargeText(toggleLargeText());

  if (error) {
    return (
      <BlockedLoad
        message="We are having trouble loading this page. You can refresh in a moment."
      />
    );
  }

  if (!content || !envelope) {
    return <PendingBanner />;
  }

  const scrollToIntro = () => {
    const el = document.getElementById("introduction");
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  // The proposal RenderGuard validates against the envelope. Fixed values
  // because the landing page's structure is static; if structure changes,
  // these counts change with it.
  const proposal: RenderProposal = {
    components: [
      "Heading",
      "Body",
      "Button",
      "Card",
      "Divider",
      "List",
    ],
    // text toggle + primary CTA + secondary CTA + up to 2 NavBar entries.
    primaryActionCount: 5,
    irreversibleActionCount: 0,
    highlightedRecommendationCount: 1, // primary CTA
    visibleTextLevels: 3, // h1, h2, body
    colorsUsed: [
      COLORS.background,
      COLORS.surface,
      COLORS.textPrimary,
      COLORS.accentMutedBlue,
      COLORS.disabled,
    ],
    spacingPxUsed: [
      SPACING.xs,
      SPACING.sm,
      SPACING.md,
      SPACING.lg,
      SPACING.xl,
      SPACING.xxl,
    ],
    radiusPxUsed: [RADIUS.sm, RADIUS.md],
    motionDurationsMs: [MOTION.defaultFadeMs],
    positionShiftPxUsed: [],
    hasUnconfirmedIrreversibleAction: false,
    usesOptimisticProgression: false,
  };

  return (
    <RenderGuard envelope={envelope} proposal={proposal}>
      <main style={PAGE}>
        <NavBar
          onSignIn={onSignIn}
          onContinuePaid={onContinuePaid}
          onAccount={onAccount}
        />
        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            marginBottom: SPACING.md,
          }}
        >
          <button
            type="button"
            onClick={handleToggleText}
            style={TEXT_TOGGLE}
            aria-pressed={largeText}
          >
            {largeText ? "Standard text" : "Larger text"}
          </button>
        </div>

        <header>
          <h1 style={H1}>{content.hero.headline}</h1>
          <p style={SUBHEAD}>{content.hero.subheadline}</p>
        </header>

        <section aria-labelledby="introduction-heading" style={SECTION}>
          <h2 id="introduction-heading" style={H2}>
            {content.introduction.title}
          </h2>
          <div id="introduction">{paragraphs(content.introduction.body)}</div>
        </section>

        <section aria-labelledby="what-noni-does-heading" style={SECTION}>
          <h2 id="what-noni-does-heading" style={H2}>
            {content.what_noni_does.title}
          </h2>
          <ul>
            {content.what_noni_does.items.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </section>

        <section aria-labelledby="how-it-feels-heading" style={SECTION}>
          <h2 id="how-it-feels-heading" style={H2}>
            {content.how_it_feels.title}
          </h2>
          <ul>
            {content.how_it_feels.items.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </section>

        <section aria-labelledby="trust-heading" style={SECTION}>
          <h2 id="trust-heading" style={H2}>
            {content.trust_and_safety.title}
          </h2>
          {paragraphs(content.trust_and_safety.body)}
        </section>

        <section aria-label="Next steps" style={CTA_GROUP}>
          <div>
            <button type="button" onClick={onBegin} style={PRIMARY_BTN}>
              {content.call_to_action.primary.label}
            </button>
            <p style={CTA_NOTE}>{content.call_to_action.primary.note}</p>
          </div>
          <div>
            <button type="button" onClick={scrollToIntro} style={SECONDARY_BTN}>
              {content.call_to_action.secondary.label}
            </button>
            <p style={CTA_NOTE}>{content.call_to_action.secondary.note}</p>
          </div>
        </section>

        <hr style={DIVIDER} />
        <footer>{paragraphs(content.closing.body)}</footer>
      </main>
    </RenderGuard>
  );
}

// Suppress unused-import warning from the FOCUS token — focus styling lives
// in styles.css so it applies system-wide, but we keep the import to anchor
// the token's owner here.
void FOCUS;
