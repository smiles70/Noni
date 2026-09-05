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

// Split backend prose on blank lines — same helper shape as HowItWorksDialog.
function paragraphs(text: string) {
  return text.split("\n\n").map((p, i) => (
    <p key={i} style={{ marginTop: 0, marginBottom: SPACING.md }}>
      {p}
    </p>
  ));
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

// Scroll affordance — calm secondary link under the primary CTA. A text link
// (not a button or icon) keeps density low and signals "more below" without
// competing with the primary action. Native anchor jump only — smooth-scroll
// would be unpermitted motion.
const MORE_LINK: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  color: COLORS.accentMutedBlue,
  textDecoration: "none",
  textAlign: "center",
  display: "inline-block",
  padding: `${SPACING.xs}px ${SPACING.sm}px`,
};

// Below-fold details — SCROLL-DEPTH-001. Renders the five API sections the
// HowItWorksDialog already uses (introduction → what it does → how it feels
// → trust & safety → closing). Pure contract inventory (Heading, Body, List,
// Divider), so it sits OUTSIDE the ADR-0029 exempt hero section but still
// inside the RenderGuard. Section titles are h2 at level2 so total text
// levels stay at 3 (exempt h1, h2, body) per the envelope limit.
const DETAILS: CSSProperties = {
  backgroundColor: COLORS.background,
  padding: `${SPACING.xxl}px ${SPACING.xl}px`,
  fontSize: TYPOGRAPHY.bodySizePx,
  lineHeight: TYPOGRAPHY.bodyLineHeight,
};

const DETAILS_INNER: CSSProperties = {
  maxWidth: 720,
  margin: "0 auto",
};

const DETAIL_SECTION: CSSProperties = {
  marginTop: SPACING.xl,
};

const DETAIL_H2: CSSProperties = {
  fontSize: TYPOGRAPHY.headingScale.level2,
  marginTop: 0,
  marginBottom: SPACING.sm,
  color: COLORS.textPrimary,
  fontWeight: 600,
};

const DETAIL_DIVIDER: CSSProperties = {
  border: "none",
  borderTop: `1px solid ${COLORS.disabled}`,
  margin: `${SPACING.xl}px 0 0`,
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
    components: ["Heading", "Body", "Button", "Card", "List", "Divider"],
    primaryActionCount: 5,
    irreversibleActionCount: 0,
    highlightedRecommendationCount: 1,
    visibleTextLevels: 3,
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
            position: "relative",
            height: "100vh",
            width: "100%",
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
                <a href="#mynaani-details" style={MORE_LINK}>
                  More about mynaani
                </a>
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

        {/* Below-fold depth — pure contract components, no exemption needed */}
        <main id="mynaani-details" style={DETAILS}>
          <div style={DETAILS_INNER}>
            <section aria-labelledby="details-introduction">
              <h2 id="details-introduction" style={DETAIL_H2}>
                {content.introduction.title}
              </h2>
              {paragraphs(content.introduction.body)}
            </section>

            <hr style={DETAIL_DIVIDER} />

            <section aria-labelledby="details-what" style={DETAIL_SECTION}>
              <h2 id="details-what" style={DETAIL_H2}>
                {content.what_mynaani_does.title}
              </h2>
              <ul>
                {content.what_mynaani_does.items.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </section>

            <hr style={DETAIL_DIVIDER} />

            <section aria-labelledby="details-feel" style={DETAIL_SECTION}>
              <h2 id="details-feel" style={DETAIL_H2}>
                {content.how_it_feels.title}
              </h2>
              <ul>
                {content.how_it_feels.items.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </section>

            <hr style={DETAIL_DIVIDER} />

            <section aria-labelledby="details-trust" style={DETAIL_SECTION}>
              <h2 id="details-trust" style={DETAIL_H2}>
                {content.trust_and_safety.title}
              </h2>
              {paragraphs(content.trust_and_safety.body)}
            </section>

            <hr style={DETAIL_DIVIDER} />

            <section style={DETAIL_SECTION}>
              {paragraphs(content.closing.body)}
            </section>
          </div>
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
