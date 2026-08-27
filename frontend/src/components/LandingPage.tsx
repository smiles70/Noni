/**
 * Landing page — contract-exempt hero renderer.
 *
 * Per ADR 0029, this page is granted a limited contract exemption:
 *   - Larger hero headings than the 1.4× body cap.
 *   - A floating action card that overlaps the hero image.
 *   - A fixed-position help bubble.
 *
 * All other application screens remain under `docs/library/CONTRACT.md`.
 * Exempt elements are marked with `data-contract-exemption="landing.hero"`
 * for audit.
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
import HowItWorksDialog from "./HowItWorksDialog";

interface Props {
  onBegin: () => void;
  onSignIn?: () => void;
  onContinuePaid?: () => void;
  onAccount?: () => void;
  signedIn?: boolean;
  onSignOut?: () => void | Promise<void>;
  onHelp?: () => void;
}

// ---- Tokenized style objects (exempt landing page only) ---------------------

const H1: CSSProperties = {
  fontSize: 32,
  marginTop: 0,
  marginBottom: SPACING.sm,
  color: COLORS.textPrimary,
  lineHeight: 1.2,
  fontWeight: 700,
};

const H2: CSSProperties = {
  fontSize: TYPOGRAPHY.headingScale.level2,
  marginTop: 0,
  marginBottom: SPACING.lg,
  color: COLORS.textPrimary,
  lineHeight: TYPOGRAPHY.bodyLineHeight,
  fontWeight: 400,
};

const NOTE: CSSProperties = {
  margin: 0,
  fontSize: TYPOGRAPHY.bodySizePx,
  color: COLORS.disabled,
};

const PRIMARY_BTN: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.md}px ${SPACING.lg}px`,
  backgroundColor: COLORS.accentDesatGreen,
  color: COLORS.surface,
  border: `2px solid ${COLORS.accentDesatGreen}`,
  borderRadius: RADIUS.lg,
  fontWeight: 600,
  cursor: "pointer",
  transition: `opacity ${MOTION.defaultFadeMs}ms ease-out`,
  width: "100%",
  textAlign: "center",
};

const SECONDARY_BTN: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.md}px ${SPACING.lg}px`,
  backgroundColor: COLORS.surface,
  color: COLORS.accentDesatGreen,
  border: `2px solid ${COLORS.accentDesatGreen}`,
  borderRadius: RADIUS.lg,
  fontWeight: 600,
  cursor: "pointer",
  transition: `opacity ${MOTION.defaultFadeMs}ms ease-out`,
  width: "100%",
  textAlign: "center",
};

const CARD: CSSProperties = {
  position: "relative",
  zIndex: 2,
  backgroundColor: COLORS.surface,
  padding: SPACING.xl,
  borderRadius: RADIUS.lg,
  boxShadow: `0 ${SPACING.md}px ${SPACING.xl}px rgba(0, 0, 0, 0.12)`,
  width: "90%",
  maxWidth: 420,
  boxSizing: "border-box",
};

const ACTION_STACK: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: SPACING.md,
};

const HELP_BUBBLE: CSSProperties = {
  position: "fixed",
  right: SPACING.xl,
  bottom: SPACING.xl,
  zIndex: 100,
  backgroundColor: COLORS.accentDesatGreen,
  color: COLORS.surface,
  padding: `${SPACING.md}px ${SPACING.lg}px`,
  borderRadius: RADIUS.lg,
  border: "none",
  fontSize: TYPOGRAPHY.bodySizePx,
  fontWeight: 600,
  cursor: "pointer",
  boxShadow: `0 ${SPACING.sm}px ${SPACING.md}px rgba(0, 0, 0, 0.15)`,
};

// ---- Loading / blocked states ----------------------------------------------

function PendingBanner() {
  return (
    <main
      style={{
        padding: SPACING.xl,
        maxWidth: 1080,
        margin: "0 auto",
        fontSize: TYPOGRAPHY.bodySizePx,
        lineHeight: TYPOGRAPHY.bodyLineHeight,
        fontFamily: TYPOGRAPHY.fontFamily,
        color: COLORS.textPrimary,
        backgroundColor: COLORS.background,
      }}
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
      style={{
        padding: SPACING.xl,
        maxWidth: 1080,
        margin: "0 auto",
        fontSize: TYPOGRAPHY.bodySizePx,
        lineHeight: TYPOGRAPHY.bodyLineHeight,
        fontFamily: TYPOGRAPHY.fontFamily,
        color: COLORS.textPrimary,
        backgroundColor: COLORS.background,
      }}
      role="alert"
      aria-live="polite"
      data-component="BlockedNotice"
    >
      <h1 style={H1}>We’re having trouble loading this page.</h1>
      <p style={{ margin: 0 }}>{message}</p>
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
    components: ["Heading", "Body", "Button", "Card"],
    primaryActionCount: 5,
    irreversibleActionCount: 0,
    highlightedRecommendationCount: 1,
    visibleTextLevels: 2,
    colorsUsed: [
      COLORS.background,
      COLORS.surface,
      COLORS.textPrimary,
      COLORS.accentDesatGreen,
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
    radiusPxUsed: [RADIUS.sm, RADIUS.md, RADIUS.lg],
    motionDurationsMs: [MOTION.defaultFadeMs],
    positionShiftPxUsed: [],
    hasUnconfirmedIrreversibleAction: false,
    usesOptimisticProgression: false,
  };

  return (
    <>
      <RenderGuard envelope={envelope} proposal={proposal}>
        <section
          data-contract-exemption="landing.hero"
          style={{
            position: "relative",
            minHeight: "100vh",
            width: "100%",
            overflow: "hidden",
            fontFamily: TYPOGRAPHY.fontFamily,
            color: COLORS.textPrimary,
          }}
        >
          {/* Full-bleed hero image */}
          <img
            src="/hero-pexels.jpg"
            alt=""
            loading="eager"
            style={{
              position: "absolute",
              top: "-7.5%",
              left: "-7.5%",
              width: "115%",
              height: "115%",
              objectFit: "cover",
              objectPosition: "25% 45%",
              zIndex: 0,
            }}
          />

          {/* Light right-side gradient so the white card reads cleanly
              without dimming the main subject. */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              background: "linear-gradient(to right, transparent 40%, rgba(0, 0, 0, 0.18) 100%)",
              zIndex: 1,
            }}
          />

          {/* Floating action card, right side */}
          <div
            data-contract-exemption="landing.hero"
            style={{
              position: "absolute",
              top: "50%",
              right: "8%",
              transform: "translateY(-50%)",
              zIndex: 2,
              width: "90%",
              maxWidth: 360,
            }}
          >
            <div style={CARD}>
              <h1 id="hero-heading" style={H1}>
                {content.hero.headline}
              </h1>
              <h2 style={H2}>{content.hero.subheadline}</h2>

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
                    {onAccount && (
                      <button
                        type="button"
                        onClick={onAccount}
                        style={SECONDARY_BTN}
                      >
                        Your account
                      </button>
                    )}
                    {onSignOut && (
                      <button
                        type="button"
                        onClick={onSignOut}
                        style={SECONDARY_BTN}
                      >
                        Sign out
                      </button>
                    )}
                    {onContinuePaid && (
                      <button
                        type="button"
                        onClick={onContinuePaid}
                        style={SECONDARY_BTN}
                      >
                        Unlock full access
                      </button>
                    )}
                    {onHelp && (
                      <button
                        type="button"
                        onClick={onHelp}
                        style={SECONDARY_BTN}
                      >
                        Help
                      </button>
                    )}
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
                    {onSignIn && (
                      <button
                        type="button"
                        onClick={onSignIn}
                        style={SECONDARY_BTN}
                      >
                        Sign in
                      </button>
                    )}
                    {onAccount && (
                      <button
                        type="button"
                        onClick={onAccount}
                        style={SECONDARY_BTN}
                      >
                        Your account
                      </button>
                    )}
                    {onHelp && (
                      <button
                        type="button"
                        onClick={onHelp}
                        style={SECONDARY_BTN}
                      >
                        Help
                      </button>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Fixed help bubble */}
          {onHelp && (
            <button
              type="button"
              onClick={onHelp}
              data-contract-exemption="landing.hero"
              style={HELP_BUBBLE}
            >
              Need help?
            </button>
          )}
        </section>
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
