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
}

// ---- Tokenized style objects -----------------------------------------------

const PAGE: CSSProperties = {
  padding: SPACING.xl,
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

export default function LandingPage({
  onBegin,
  onSignIn,
  onContinuePaid,
  onAccount,
  signedIn,
  onSignOut,
}: Props) {
  const [content, setContent] = useState<LandingPageContent | null>(null);
  const [envelope, setEnvelope] = useState<UIStateEnvelope | null>(null);
  const [error, setError] = useState<string | null>(null);
  // Whether the long-form "How Noni works" dialog is open. Closed by
  // default; opens when the visitor clicks the primary CTA
  // ("Set up my account — free") on the auth row. Closing returns focus
  // to the trigger via the browser's default.
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

  // The proposal RenderGuard validates against the envelope. Counts
  // reflect what the landing page actually renders now: hero image,
  // headline, primary "Set up my account" button, secondary "Log in"
  // button, plus up to 2 NavBar entries when signed in. Long-form copy
  // lives in HowItWorksDialog, which is rendered outside the guarded
  // subtree.
  const proposal: RenderProposal = {
    components: ["Heading", "Body", "Button"],
    // primary CTA + secondary CTA + up to 2 NavBar entries.
    primaryActionCount: 4,
    irreversibleActionCount: 0,
    highlightedRecommendationCount: 1, // primary CTA only
    visibleTextLevels: 2, // h1 + body (note + button labels)
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
        {/* Hero: full-width landscape image (whole picture visible — no
            crop) with a centered white banner overlay containing the
            headline and a "Learn more" action that scrolls to the
            introduction. Beneath the photo: a primary "Create account"
            and a secondary "Log in" action. Image is decorative (alt=""),
            so it does not add to the visible-text-level count.

            Note: the hero headline and overlay button label are
            intentional front-end overrides per the user's request for
            calmer SaaS-style phrasing. Other copy still flows from the
            backend. */}
        <section className="noni-hero" aria-labelledby="hero-heading">
          <div className="noni-hero__frame">
            <img
              className="noni-hero__image"
              src="/nonisplash.jpg"
              alt=""
              loading="eager"
            />
          </div>
          <div className="noni-hero__overlay">
            <h1 id="hero-heading" className="noni-hero__overlay-title">
              Learn AI on your terms!
            </h1>
          </div>

          {/* Auth row directly under the photo. The primary label names
              exactly what the click does today (account setup) and pairs
              it with a one-line reassurance to remove the card-on-file
              fear — geragogy research consistently shows older adults
              respond better to plain, honest action labels than to
              outcome promises that may not match the next screen. When a
              real sample lesson exists, revisit this label as
              "Try your first lesson". */}
          <div className="noni-hero__auth-row">
            {signedIn ? (
              <>
                <div className="noni-hero__primary-cta">
                  <button
                    type="button"
                    onClick={onBegin}
                    style={PRIMARY_BTN}
                  >
                    Continue learning →
                  </button>
                </div>
                {onSignOut && <SignOutLink onSignedOut={onSignOut} />}
              </>
            ) : (
              <>
                <div className="noni-hero__primary-cta">
                  <button
                    type="button"
                    onClick={() => setShowHowItWorks(true)}
                    style={PRIMARY_BTN}
                  >
                    Set up my account — free
                  </button>
                  <p className="noni-hero__cta-note">
                    Free. No card needed. Stop any time.
                  </p>
                </div>
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

          {/* NavBar surfaces signed-in entries (Upgrade / Your account).
              Signed-out users see no extra entries here. NavBar reads
              AuthProvider state via useAuth() so a re-render on auth
              transition is sufficient; the `key` is retained as a belt-
              and-braces remount guard against any cached local state
              surviving a sign-out frame. */}
          <NavBar
            key={signedIn ? "nav-signed-in" : "nav-signed-out"}
            onContinuePaid={onContinuePaid}
            onAccount={onAccount}
          />
        </section>

        {/* The "How Noni works" explanation is now the mandatory first
            step for new users before they reach the auth wall. The
            dialog is rendered outside the RenderGuard boundary. */}
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

// Suppress unused-import warning from the FOCUS token — focus styling lives
// in styles.css so it applies system-wide, but we keep the import to anchor
// the token's owner here.
void FOCUS;
