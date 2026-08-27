/**
 * WelcomePage - Account setup welcome screen (EPIC-002 Phase 2)
 *
 * Geragogy-compliant welcome screen shown after successful authentication.
 * Provides a calm, dignified introduction to account setup with clear
 * next steps and minimal cognitive load.
 *
 * Key geragogy principles:
 * - Predictable interface with stable layout
 * - Calm, dignified tone without urgency
 * - Clear next steps with minimal decisions
 * - Maximum 3 text levels visible
 * - Maximum 5 primary actionable elements
 * - No irreversible actions without confirmation
 */
import { useState, useEffect } from "react";
import { apiClient } from "../api/client";
import { loadEnvelope } from "../api/envelope";
import { RenderGuard, type RenderProposal } from "../design/RenderGuard";
import { COLORS, MOTION, RADIUS, SPACING } from "../design/tokens";
import type { UIStateEnvelope } from "../design/envelope";
import {
  BODY,
  CARD,
  DIVIDER,
  H1,
  H2,
  PAGE,
  PRIMARY_BTN,
  SECONDARY_BTN,
  STACK,
} from "./AccountStyles";
import { onboardingTelemetry } from "../lib/onboardingTelemetry";

interface Props {
  onContinue: () => void;
  onAccount: () => void;
  onAccountSetup: () => void;
  onSignOut: () => Promise<void>;
}

interface OnboardingStatus {
  account_id: string;
  onboarding_complete: boolean;
  display_name: string | null;
  preferences_set: boolean;
}

export default function WelcomePage({
  onContinue,
  onAccount,
  onAccountSetup,
  onSignOut,
}: Props) {
  const [envelope, setEnvelope] = useState<UIStateEnvelope | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [checkingStatus, setCheckingStatus] = useState(true);

  useEffect(() => {
    // EPIC-002 Phase 2: Check onboarding status first
    const checkOnboardingStatus = async () => {
      try {
        const res = await apiClient.get<OnboardingStatus>(
          "/account/onboarding-status",
        );
        if (res.data.onboarding_complete) {
          // User already completed onboarding, go directly to curriculum
          onContinue();
          return;
        } else {
          // User needs to complete onboarding, go to account setup
          onAccountSetup();
          return;
        }
      } catch (err) {
        // If status check fails, continue to welcome page
        console.error("Failed to check onboarding status:", err);
      } finally {
        setCheckingStatus(false);
      }

      // Load envelope after status check
      loadEnvelope("account.welcome")
        .then((env) => {
          setEnvelope(env);
          setLoading(false);
          // EPIC-002 Phase 4: Track welcome page view
          onboardingTelemetry.trackWelcomeView();
        })
        .catch(() => {
          setError("Please wait a moment and refresh the page.");
          setLoading(false);
        });
    };

    checkOnboardingStatus();
  }, [onContinue, onAccountSetup]);

  if (loading || checkingStatus) {
    return (
      <main style={PAGE} aria-live="polite" data-component="PendingBanner">
        <p style={BODY}>One moment — loading the welcome page.</p>
      </main>
    );
  }

  if (error) {
    return (
      <main style={PAGE} role="alert" data-component="BlockedNotice">
        <h1 style={H1}>We’re having trouble loading this page.</h1>
        <p style={BODY}>{error}</p>
        <button
          type="button"
          style={PRIMARY_BTN}
          onClick={() => window.location.reload()}
        >
          Try again
        </button>
      </main>
    );
  }

  if (!envelope) {
    return (
      <main style={PAGE} aria-live="polite" data-component="PendingBanner">
        <p style={BODY}>One moment — loading the welcome page.</p>
      </main>
    );
  }

  const proposal: RenderProposal = {
    components: ["Heading", "Body", "Button", "Card", "Divider"],
    primaryActionCount: 2,
    irreversibleActionCount: 0,
    highlightedRecommendationCount: 1,
    visibleTextLevels: 2,
    colorsUsed: [
      COLORS.background,
      COLORS.surface,
      COLORS.textPrimary,
      COLORS.accentMutedBlue,
      COLORS.disabled,
    ],
    spacingPxUsed: [SPACING.xs, SPACING.sm, SPACING.md, SPACING.lg, SPACING.xl],
    radiusPxUsed: [RADIUS.sm, RADIUS.md],
    motionDurationsMs: [MOTION.defaultFadeMs],
    positionShiftPxUsed: [],
    hasUnconfirmedIrreversibleAction: false,
    usesOptimisticProgression: false,
  };

  const handleSignOut = async () => {
    await onSignOut();
  };

  return (
    <RenderGuard envelope={envelope} proposal={proposal}>
      <main style={PAGE}>
        <h1 style={H1}>Welcome to Mynaani</h1>

        <p style={BODY}>
          You have successfully signed in. We will now set up your account so
          you can save your progress and continue where you left off.
        </p>

        <div style={CARD}>
          <h2 style={H2}>What happens next</h2>
          <p style={BODY}>
            You will complete a short setup to add your name and preferences.
            This takes about 2 minutes. After that, you can begin learning at
            your own pace.
          </p>
        </div>

        <div style={CARD}>
          <h2 style={H2}>Why we ask for this information</h2>
          <p style={BODY}>
            Your name helps us personalize your experience. Your preferences
            help us show you content that matches how you like to learn. You can
            change these settings at any time from your account page.
          </p>
        </div>

        <div style={STACK}>
          <button type="button" style={PRIMARY_BTN} onClick={onContinue}>
            Continue to account setup
          </button>
          <button type="button" style={SECONDARY_BTN} onClick={onAccount}>
            Go to account settings
          </button>
          <button type="button" style={SECONDARY_BTN} onClick={handleSignOut}>
            Sign out
          </button>
        </div>

        <hr style={DIVIDER} />
        <p style={BODY}>
          Signing in lets us save your progress and remember what works for you.
          You can sign out from your account page at any time.
        </p>
      </main>
    </RenderGuard>
  );
}
