/**
 * Landing page — contract-exempt hero renderer.
 *
 * Per ADR 0029, this page is granted a limited contract exemption:
 *   - Larger hero headings than the 1.4× body cap.
 *   - A floating action card that overlaps the hero image.
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
import LandingFooter from "./LandingFooter";

interface Props {
  onBegin: () => void;
  signedIn?: boolean;
}

// ---- Tokenized style objects (exempt landing page only) ---------------------

const H1: CSSProperties = {
  fontSize: 40,
  marginTop: 0,
  marginBottom: SPACING.sm,
  color: COLORS.textPrimary,
  lineHeight: 1.2,
  fontWeight: 800,
};

const H2: CSSProperties = {
  // Bumped to level1 for the hero only — the subheadline reads as a
  // statement line under the headline per the approved mock.
  fontSize: TYPOGRAPHY.headingScale.level1,
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

// Legibility wash — a left-to-right surface gradient over the hero photo
// so the headline keeps its contrast ratio without a card. Near-solid on
// mobile where the photo crops narrow (per the approved mock).
const GRADIENT_WASH: CSSProperties = {
  position: "absolute",
  inset: 0,
  zIndex: 1,
  background:
    "linear-gradient(to right, rgba(250, 250, 248, 0.92) 0%, rgba(250, 250, 248, 0.6) 45%, rgba(250, 250, 248, 0) 70%)",
  pointerEvents: "none",
};

const GRADIENT_WASH_MOBILE: CSSProperties = {
  ...GRADIENT_WASH,
  background: "rgba(250, 250, 248, 0.95)",
};

// Hero copy sits directly on the wash — left-aligned, vertically centred.
const HERO_CONTENT: CSSProperties = {
  position: "absolute",
  top: "50%",
  left: "5%",
  transform: "translateY(-50%)",
  zIndex: 2,
  width: "90%",
  // Narrow column so the subheadline wraps short of the photo's faces
  // on the right (per the approved mock).
  maxWidth: 340,
};

const HERO_CONTENT_MOBILE: CSSProperties = {
  ...HERO_CONTENT,
  left: SPACING.lg,
  right: SPACING.lg,
  width: "auto",
};

// Mock CTA is inline-block, sized to its label — not a full-width card button.
const HERO_BTN: CSSProperties = {
  ...PRIMARY_BTN,
  width: "auto",
  minWidth: 240,
  alignSelf: "flex-start",
};

const ACTION_STACK: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: SPACING.md,
};

// Brand mark — bare logo floating in the upper-left corner, no plate or
// well. The legibility wash underneath supplies the separation from the
// photo. Must sit above GRADIENT_WASH (zIndex 1) so the wash does not dim it.
const LOGO_PLATE: CSSProperties = {
  position: "absolute",
  top: SPACING.md,
  left: SPACING.lg,
  zIndex: 3,
};

const LOGO_PLATE_MOBILE: CSSProperties = {
  ...LOGO_PLATE,
  top: SPACING.sm,
  left: SPACING.md,
};

// Logo heights used for both the mark and the hero top offset.
const LOGO_IMG_HEIGHT = 120;
const LOGO_IMG_HEIGHT_MOBILE = 88;

// Stacked ~1:1 lockup, so height is fixed and width derives from the asset
// (921×957). Sizes honour the 8px grid: 120px desktop (15×8) / 88px mobile
// (11×8). Non-interactive: this page is already home, and adding a link would
// add an actionable element for no gain.
const LOGO_IMG: CSSProperties = {
  display: "block",
  height: LOGO_IMG_HEIGHT,
  width: "auto",
};

const LOGO_IMG_MOBILE: CSSProperties = {
  ...LOGO_IMG,
  height: LOGO_IMG_HEIGHT_MOBILE,
};

// Hero image is full-bleed; the light top overlay now sits on top of it.
const PICTURE_TOP = 0;
const PICTURE_TOP_MOBILE = 0;

// B2B pathway — primary-style enterprise route stack at top-right.
// The hero stays visually unchanged for learners; institutional visitors
// get clearly labelled routes without a prohibited dropdown.
const B2B_BUTTON: CSSProperties = {
  // B2B-ENTRY-001: same shape as the primary CTA — centered, fixed
  // green button with 44px touch target and 2px border.
  display: "inline-flex",
  justifyContent: "center",
  alignItems: "center",
  textAlign: "center",
  whiteSpace: "nowrap",
  minHeight: 44,
  width: 200,
  boxSizing: "border-box",
  padding: `${SPACING.md}px ${SPACING.lg}px`,
  backgroundColor: COLORS.accentDesatGreen,
  borderRadius: RADIUS.lg,
  border: `2px solid ${COLORS.accentDesatGreen}`,
  color: COLORS.surface,
  textDecoration: "none",
  fontSize: TYPOGRAPHY.bodySizePx,
  fontWeight: 600,
  cursor: "pointer",
  transition: `opacity ${MOTION.defaultFadeMs}ms ease-out`,
};

const B2B_STACK: CSSProperties = {
  position: "absolute",
  top: SPACING.xl,
  right: SPACING.xl,
  zIndex: 1,
  display: "inline-flex",
  alignItems: "center",
  gap: SPACING.md,
};

const B2B_STACK_MOBILE: CSSProperties = {
  ...B2B_STACK,
  top: SPACING.lg,
  right: SPACING.lg,
  flexDirection: "column",
  gap: SPACING.sm,
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

export default function LandingPage({ onBegin, signedIn }: Props) {
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
    components: ["Heading", "Body", "Button"],
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
  const heroContentStyle: CSSProperties = isMobile
    ? HERO_CONTENT_MOBILE
    : HERO_CONTENT;

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
          {/* Hero image — full-bleed, art-directed for mobile */}
          <picture
            style={{
              position: "absolute",
              top: isMobile ? PICTURE_TOP_MOBILE : PICTURE_TOP,
              left: 0,
              width: "100%",
              height: isMobile
                ? `calc(100% - ${PICTURE_TOP_MOBILE}px)`
                : `calc(100% - ${PICTURE_TOP}px)`,
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
                // Anchor subjects to the right so the left-side copy
                // never collides with faces (mock: center right).
                objectPosition: isMobile ? "center" : "right center",
              }}
            />
          </picture>

          {/* Brand mark floating on the wash — upper-left landmark */}
          <div
            style={isMobile ? LOGO_PLATE_MOBILE : LOGO_PLATE}
            data-contract-exemption="landing.hero"
            data-brand-plate="landing.hero"
          >
            <img
              src="/mynaani-logo.webp"
              alt="mynaani"
              width={115}
              height={120}
              style={isMobile ? LOGO_IMG_MOBILE : LOGO_IMG}
              data-contract-exemption="landing.hero"
            />
          </div>

          {/* Legibility wash between photo and copy */}
          <div
            style={isMobile ? GRADIENT_WASH_MOBILE : GRADIENT_WASH}
            data-contract-exemption="landing.hero"
            aria-hidden="true"
          />

          {/* Hero copy — left-aligned on the wash */}
          <div data-contract-exemption="landing.hero" style={heroContentStyle}>
            <h1 id="hero-heading" style={h1Style}>
              {content.hero.headline}
            </h1>
            <h2 style={H2}>{content.hero.subheadline}</h2>

            <div style={ACTION_STACK}>
              {signedIn ? (
                <button type="button" onClick={onBegin} style={HERO_BTN}>
                  Continue learning →
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => setShowHowItWorks(true)}
                  style={HERO_BTN}
                >
                  {content.call_to_action.primary.label}
                </button>
              )}
            </div>
          </div>

          {/* B2B pathway — top-right primary-style links, exempt marketing route */}
          <div
            style={isMobile ? B2B_STACK_MOBILE : B2B_STACK}
            data-contract-exemption="landing.hero"
            data-b2b-stack="hero"
          >
            <Link
              to="/caregiver"
              style={B2B_BUTTON}
              data-contract-exemption="landing.hero"
              data-caregiver-entry="hero"
              aria-label="Caregiver — learn about giving mynaani as a gift"
            >
              Caregiver
            </Link>
            <Link
              to="/for-communities"
              style={B2B_BUTTON}
              data-contract-exemption="landing.hero"
              data-b2b-entry="hero"
              aria-label="Senior facilities — the mynaani enterprise pathway"
            >
              Senior facilities
            </Link>
          </div>
        </section>
        {/* LEGAL-NAV-001: mini-footer strip — legal links pinned inside
            the fixed viewport. Sibling of the hero <section> so it keeps
            its contentinfo landmark role. */}
        <LandingFooter />
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
