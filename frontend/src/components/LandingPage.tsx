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
import { Link } from "react-router-dom";
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
import { TYPE_SCALE } from "../styles/responsiveTokens";
import { useViewport } from "../hooks/useViewport";
import type { UIStateEnvelope } from "../design/envelope";
import { RenderGuard, type RenderProposal } from "../design/RenderGuard";
import HowItWorksDialog from "./HowItWorksDialog";

interface Props {
  onBegin: () => void;
  signedIn?: boolean;
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

const CARD: CSSProperties = {
  position: "relative",
  zIndex: 2,
  backgroundColor: "rgba(250, 250, 248, 0.5)",
  padding: SPACING.lg,
  borderRadius: RADIUS.lg,
  boxShadow: `0 ${SPACING.md}px ${SPACING.xl}px rgba(0, 0, 0, 0.12)`,
  width: "100%",
  maxWidth: 320,
  boxSizing: "border-box",
};

const ACTION_STACK: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: SPACING.md,
};

// Brand plate — top-left of the hero. The muted mark needs separation from
// the photo's dark region to remain legible for presbyopic users and to read
// as an identity/legitimacy signal (BRAND-LOGO-002 findings F1–F3). The plate
// reuses the action card's surface family (COLORS.surface at 85% opacity),
// RADIUS.lg corners, SPACING.sm clear space — no new tokens, no shadow, no
// motion. Position stays the NN/g-validated top-left landmark.
const LOGO_PLATE: CSSProperties = {
  position: "absolute",
  top: SPACING.xl,
  left: SPACING.xl,
  zIndex: 1,
  padding: SPACING.sm,
  backgroundColor: "rgba(250, 250, 248, 0.85)",
  borderRadius: RADIUS.lg,
};

const LOGO_PLATE_MOBILE: CSSProperties = {
  ...LOGO_PLATE,
  top: SPACING.lg,
  left: SPACING.lg,
};

// Stacked ~1:1 lockup, so height is fixed and width derives from the asset
// (921×957). Sizes honour the 8px grid: 128px desktop (16×8) / 96px mobile
// (12×8). Non-interactive: this page is already home, and adding a link would
// add an actionable element for no gain.
const LOGO_IMG: CSSProperties = {
  display: "block",
  height: 128,
  width: "auto",
};

const LOGO_IMG_MOBILE: CSSProperties = {
  ...LOGO_IMG,
  height: 96,
};

// B2B pathway — Candoo-pattern entry: a calm text link top-right on a
// surface plate (same treatment family as the brand plate). The hero stays
// visually unchanged for learners; institutional visitors get a clearly
// labelled route to /for-communities without a prohibited dropdown.
const B2B_ENTRY: CSSProperties = {
  position: "absolute",
  top: SPACING.xl,
  right: SPACING.xl,
  zIndex: 1,
  // B2B-ENTRY-001: ≥44px target + inline-flex for a11y polish.
  display: "inline-flex",
  alignItems: "center",
  minHeight: 44,
  padding: `${SPACING.sm}px ${SPACING.md}px`,
  backgroundColor: "rgba(250, 250, 248, 0.85)",
  borderRadius: RADIUS.lg,
  // B2B-ENTRY-001 gap fix: ghost-button border gives the enterprise
  // affordance every audited best-in-class SaaS nav uses, while the
  // muted treatment keeps it correctly secondary to the primary CTA.
  border: `1px solid ${COLORS.accentMutedBlue}`,
  color: COLORS.accentMutedBlue,
  textDecoration: "none",
  fontSize: TYPOGRAPHY.bodySizePx,
};

const B2B_ENTRY_MOBILE: CSSProperties = {
  ...B2B_ENTRY,
  top: SPACING.lg,
  right: SPACING.lg,
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

export default function LandingPage({ onBegin, signedIn, onHelp }: Props) {
  const [content, setContent] = useState<LandingPageContent | null>(null);
  const [envelope, setEnvelope] = useState<UIStateEnvelope | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showHowItWorks, setShowHowItWorks] = useState(false);
  const { isMobile } = useViewport();

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
      <BlockedLoad message="We are having trouble loading this page. You can refresh in a moment." />
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

  const h1Style: CSSProperties = isMobile
    ? { ...H1, fontSize: TYPE_SCALE.mobile.h1 }
    : H1;
  const cardStyle: CSSProperties = isMobile
    ? {
        ...CARD,
        padding: SPACING.md,
        maxHeight: "calc(45% - 96px)",
        overflowY: "auto",
      }
    : CARD;
  const cardPosition: CSSProperties = isMobile
    ? {
        position: "absolute",
        top: "55%",
        left: "50%",
        transform: "translateX(-50%)",
        zIndex: 2,
        width: "92%",
        maxWidth: 320,
      }
    : {
        position: "absolute",
        top: "50%",
        right: "4%",
        transform: "translateY(-50%)",
        zIndex: 2,
        width: "90%",
        maxWidth: 340,
      };

  return (
    <>
      <RenderGuard envelope={envelope} proposal={proposal}>
        <section
          data-contract-exemption="landing.hero"
          style={{
            position: "fixed",
            inset: 0,
            overflow: "hidden",
            fontFamily: TYPOGRAPHY.fontFamily,
            color: COLORS.textPrimary,
          }}
        >
          {/* Full-bleed hero image — art-directed for mobile */}
          <picture
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
              zIndex: 0,
            }}
          >
            <source
              media="(max-width: 767px)"
              srcSet="/hero-mobile.jpg"
              type="image/jpeg"
            />
            <img
              src="/hero-mynaani.jpg"
              alt=""
              loading="eager"
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                objectPosition: "center center",
              }}
            />
          </picture>

          {/* Brand mark on a calm surface plate — upper-left landmark */}
          <div
            style={isMobile ? LOGO_PLATE_MOBILE : LOGO_PLATE}
            data-contract-exemption="landing.hero"
            data-brand-plate="landing.hero"
          >
            <img
              src="/mynaani-logo.webp"
              alt="mynaani"
              width={123}
              height={128}
              style={isMobile ? LOGO_IMG_MOBILE : LOGO_IMG}
              data-contract-exemption="landing.hero"
            />
          </div>

          {/* Floating action card, right side */}
          <div data-contract-exemption="landing.hero" style={cardPosition}>
            <div style={cardStyle}>
              <h1 id="hero-heading" style={h1Style}>
                {content.hero.headline}
              </h1>
              <h2 style={H2}>{content.hero.subheadline}</h2>

              <div style={ACTION_STACK}>
                {signedIn ? (
                  <button type="button" onClick={onBegin} style={PRIMARY_BTN}>
                    Continue learning →
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={() => setShowHowItWorks(true)}
                    style={PRIMARY_BTN}
                  >
                    {content.call_to_action.primary.label}
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* B2B pathway — top-right text link, exempt marketing route */}
          <Link
            to="/for-communities"
            style={isMobile ? B2B_ENTRY_MOBILE : B2B_ENTRY}
            data-contract-exemption="landing.hero"
            data-b2b-entry="hero"
            aria-label="For senior living communities — the mynaani enterprise pathway"
          >
            For senior living communities
          </Link>

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
