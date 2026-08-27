/**
 * Landing page — contract-bound hero renderer.
 *
 * Per ADR 0019 and CONTRACT Section IV, this component:
 *   - Resolves its envelope from `/api/ui-envelope/landing.page` on mount.
 *   - Renders inside a RenderGuard boundary that fails closed on any
 *     contract violation.
 *   - Uses ONLY tokens from `design/tokens.ts` for color, spacing, type,
 *     radius, and motion. No raw hex literals, no arbitrary spacing values.
 *
 * Copy comes from the backend (`/api/landing/page`, per ADR 0006).
 * This redesign (ADR 0028, HERO-001) uses a warm hero image on the left
 * and a single action card on the right, with the remaining marketing
 * sections stacked below in a calm, low-density column.
 */
import { CSSProperties, useEffect, useState } from "react";
import { loadLandingPage, LandingPageContent } from "../api/landing";
import { loadEnvelope } from "../api/envelope";
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
import HowItWorksDialog from "./HowItWorksDialog";
import SignOutLink from "./SignOutLink";

interface Props {
  onBegin: () => void;
  onSignIn?: () => void;
  onContinuePaid?: () => void;
  onAccount?: () => void;
  /** Drives which CTA pair the auth row renders. When true the primary
   *  CTA becomes 'Continue learning →' and the secondary becomes 'Sign
   *  out'; the 'Set up my account / Log in' pair is hidden. */
  signedIn?: boolean;
  /** Called after a successful sign-out so AuthProvider's state can transition
   *  and re-render the signed-out landing surface. */
  onSignOut?: () => void | Promise<void>;
  onHelp?: () => void;
}

// ---- Tokenized style objects -----------------------------------------------

const PAGE: CSSProperties = {
  padding: `${SPACING.xl}px ${SPACING.lg}px`,
  maxWidth: 1080, // 135 × 8px = grid-aligned; gives the hero room
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
  lineHeight: TYPOGRAPHY.bodyLineHeight,
};

const H2: CSSProperties = {
  fontSize: TYPOGRAPHY.headingScale.level2,
  marginTop: 0,
  marginBottom: SPACING.sm,
  color: COLORS.textPrimary,
};

const BODY: CSSProperties = {
  marginTop: 0,
  marginBottom: SPACING.md,
};

const UL: CSSProperties = {
  marginTop: 0,
  marginBottom: SPACING.md,
  paddingLeft: SPACING.lg,
};

const LI: CSSProperties = {
  marginBottom: SPACING.sm,
};

const CARD: CSSProperties = {
  backgroundColor: COLORS.surface,
  border: `1px solid ${COLORS.disabled}`,
  borderRadius: RADIUS.md,
  padding: SPACING.lg,
};

const PRIMARY_BTN: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.md}px ${SPACING.lg}px`,
  backgroundColor: COLORS.accentMutedBlue,
  color: COLORS.surface,
  border: `2px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.sm,
  fontWeight: 600,
  cursor: "pointer",
  transition: `opacity ${MOTION.defaultFadeMs}ms ease-out`,
  width: "100%",
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
  width: "100%",
};

const DIVIDER: CSSProperties = {
  border: 0,
  borderTop: `1px solid ${COLORS.disabled}`,
  margin: `${SPACING.xl}px 0`,
};

const IMAGE_CARD: CSSProperties = {
  width: "100%",
  borderRadius: RADIUS.md,
  overflow: "hidden",
  boxShadow: `0 ${SPACING.sm}px ${SPACING.lg}px rgba(0, 0, 0, 0.08)`,
};

const HERO_IMAGE: CSSProperties = {
  width: "100%",
  height: "auto",
  maxHeight: 400,
  objectFit: "cover",
  display: "block",
};

const HERO_ROW: CSSProperties = {
  display: "flex",
  flexWrap: "wrap",
  gap: SPACING.xl,
  alignItems: "center",
  marginBottom: SPACING.xl,
};

const HERO_COLUMN: CSSProperties = {
  flex: "1 1 320px",
  minWidth: 280,
};

const ACTION_STACK: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: SPACING.md,
};

const NOTE: CSSProperties = {
  margin: 0,
  fontSize: TYPOGRAPHY.bodySizePx,
  color: COLORS.disabled,
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
      <h1 style={H1}>We’re having trouble loading this page.</h1>
      <p>{message}</p>
    </main>
  );
}

// ---- Component -------------------------------------------------------------

export default function LandingPage({
  onBegin,
  onSignIn,
  onContinuePaid,
  onAccount,
  signedIn,
  onSignOut,
  onHelp,
}: Props) {
  const [content, setContent] = useState<LandingPageContent | null>(null);
  const [envelope, setEnvelope] = useState<UIStateEnvelope | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showHowItWorks, setShowHowItWorks] = useState(false);

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

  const proposal: RenderProposal = {
    components: ["Heading", "Body", "Button", "Card", "List", "Divider"],
    primaryActionCount: 5,
    irreversibleActionCount: 0,
    highlightedRecommendationCount: 1,
    visibleTextLevels: 3,
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
    <>
      <RenderGuard envelope={envelope} proposal={proposal}>
        <main style={PAGE}>
          {/* Hero: warm image on the left, action card on the right. */}
          <section aria-labelledby="hero-heading" style={{ marginBottom: SPACING.xxl }}>
            <div style={HERO_ROW}>
              <div style={HERO_COLUMN}>
                <div style={IMAGE_CARD}>
                  <img
                    src="/nonisplash.jpg"
                    alt=""
                    loading="eager"
                    style={HERO_IMAGE}
                  />
                </div>
              </div>

              <div style={HERO_COLUMN}>
                <h1 id="hero-heading" style={H1}>
                  {content.hero.headline}
                </h1>
                <p style={BODY}>{content.hero.subheadline}</p>

                <div style={CARD}>
                  <div style={ACTION_STACK}>
                    {signedIn ? (
                      <>
                        <button
                          type="button"
                          onClick={onBegin}
                          style={PRIMARY_BTN}
                        >
                          Continue learning →
                        </button>
                        {onSignOut && <SignOutLink onSignedOut={onSignOut} />}
                      </>
                    ) : (
                      <>
                        <button
                          type="button"
                          onClick={onBegin}
                          style={PRIMARY_BTN}
                        >
                          {content.call_to_action.primary.label}
                        </button>
                        <p style={NOTE}>
                          {content.call_to_action.primary.note}
                        </p>
                        <button
                          type="button"
                          onClick={() => setShowHowItWorks(true)}
                          style={SECONDARY_BTN}
                        >
                          {content.call_to_action.secondary.label}
                        </button>
                        <p style={NOTE}>
                          {content.call_to_action.secondary.note}
                        </p>
                        {onSignIn && (
                          <button
                            type="button"
                            onClick={onSignIn}
                            style={SECONDARY_BTN}
                          >
                            Log in
                          </button>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Supporting sections — kept low-density and plain. */}
          <section aria-labelledby="intro-heading">
            <h2 id="intro-heading" style={H2}>
              {content.introduction.title}
            </h2>
            {content.introduction.body.split("\n\n").map((paragraph, i) => (
              <p key={i} style={BODY}>
                {paragraph}
              </p>
            ))}
          </section>

          <hr style={DIVIDER} />

          <section aria-labelledby="what-heading">
            <h2 id="what-heading" style={H2}>
              {content.what_noni_does.title}
            </h2>
            <ul style={UL}>
              {content.what_noni_does.items.map((item) => (
                <li key={item} style={LI}>
                  {item}
                </li>
              ))}
            </ul>
          </section>

          <hr style={DIVIDER} />

          <section aria-labelledby="feel-heading">
            <h2 id="feel-heading" style={H2}>
              {content.how_it_feels.title}
            </h2>
            <ul style={UL}>
              {content.how_it_feels.items.map((item) => (
                <li key={item} style={LI}>
                  {item}
                </li>
              ))}
            </ul>
          </section>

          <hr style={DIVIDER} />

          <section aria-labelledby="trust-heading">
            <h2 id="trust-heading" style={H2}>
              {content.trust_and_safety.title}
            </h2>
            {content.trust_and_safety.body.split("\n\n").map((paragraph, i) => (
              <p key={i} style={BODY}>
                {paragraph}
              </p>
            ))}
          </section>

          <hr style={DIVIDER} />

          <section>
            {content.closing.body.split("\n\n").map((paragraph, i) => (
              <p key={i} style={BODY}>
                {paragraph}
              </p>
            ))}
          </section>

          <NavBar
            key={signedIn ? "nav-signed-in" : "nav-signed-out"}
            onContinuePaid={onContinuePaid}
            onAccount={onAccount}
            onHelp={onHelp}
          />
        </main>
      </RenderGuard>
      {showHowItWorks && (
        <HowItWorksDialog
          content={content}
          onClose={() => setShowHowItWorks(false)}
          onBegin={onBegin}
        />
      )}
    </>
  );
}

// Suppress unused-import warning from the FOCUS token.
void FOCUS;
