/**
 * GettingStartedPage - Progressive onboarding guidance (EPIC-002 Phase 3)
 *
 * Geragogy-compliant progressive onboarding page that guides users through
 * their first meaningful action with clear, step-by-step guidance.
 *
 * Key geragogy principles:
 * - Predictable interface with stable layout
 * - Calm, dignified tone without urgency
 * - Clear step-by-step guidance
 * - Maximum 3 text levels visible
 * - Maximum 5 primary actionable elements
 * - No irreversible actions without confirmation
 * - Celebrates first meaningful action completion
 */
import { useState, useEffect } from "react";
import { loadEnvelope } from "../api/envelope";
import { RenderGuard, type RenderProposal } from "../design/RenderGuard";
import {
  COLORS,
  MOTION,
  RADIUS,
  SPACING,
  TYPOGRAPHY,
} from "../design/tokens";
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
  SUCCESS_TEXT,
} from "./AccountStyles";
import { onboardingTelemetry } from "../lib/onboardingTelemetry";

interface Props {
  onContinue: () => void;
  onBack: () => void;
  onSignOut: () => Promise<void>;
}

export default function GettingStartedPage({ onContinue, onBack, onSignOut }: Props) {
  const [envelope, setEnvelope] = useState<UIStateEnvelope | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [completed, setCompleted] = useState(false);

  const steps = [
    {
      title: "Welcome to your learning journey",
      description: "You are about to start Module 1, which introduces the basics of AI. This module is designed for beginners and takes about 30 minutes to complete.",
      action: "Start Module 1",
    },
    {
      title: "How to navigate",
      description: "Use the Next button to move through each lesson. You can go back to review previous lessons at any time. Your progress is saved automatically.",
      action: "Continue",
    },
    {
      title: "Your first lesson",
      description: "The first lesson explains what AI is and how it works. You will learn at your own pace with clear explanations and examples.",
      action: "Begin learning",
    },
  ];

  useEffect(() => {
    loadEnvelope("account.getting-started")
      .then((env) => {
        setEnvelope(env);
        setLoading(false);
        // EPIC-002 Phase 4: Track getting started view
        onboardingTelemetry.trackGettingStartedView();
      })
      .catch(() => {
        setError("Please wait a moment and refresh the page.");
        setLoading(false);
      });
  }, []);

  const handleNextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      setCompleted(true);
      // EPIC-002 Phase 4: Track getting started completion
      onboardingTelemetry.trackGettingStartedComplete();
      // Auto-continue after celebration
      setTimeout(() => {
        onContinue();
      }, 3000);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    } else {
      onBack();
    }
  };

  const handleSignOut = async () => {
    await onSignOut();
  };

  if (loading) {
    return (
      <main style={PAGE} aria-live="polite" data-component="PendingBanner">
        <p style={BODY}>One moment — loading the getting started page.</p>
      </main>
    );
  }

  if (error && !envelope) {
    return (
      <main style={PAGE} role="alert" data-component="BlockedNotice">
        <h1 style={H1}>This page is paused.</h1>
        <p style={BODY}>{error}</p>
      </main>
    );
  }

  if (!envelope) {
    return (
      <main style={PAGE} aria-live="polite" data-component="PendingBanner">
        <p style={BODY}>One moment — loading the getting started page.</p>
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
      COLORS.accentDesatGreen,
    ],
    spacingPxUsed: [SPACING.xs, SPACING.sm, SPACING.md, SPACING.lg, SPACING.xl],
    radiusPxUsed: [RADIUS.sm, RADIUS.md],
    motionDurationsMs: [MOTION.defaultFadeMs],
    positionShiftPxUsed: [],
    hasUnconfirmedIrreversibleAction: false,
    usesOptimisticProgression: false,
  };

  if (completed) {
    return (
      <RenderGuard envelope={envelope} proposal={proposal}>
        <main style={PAGE}>
          <h1 style={H1}>You are ready to begin</h1>
          <p style={SUCCESS_TEXT}>
            You have completed the getting started guide. You will now begin
            Module 1. Your progress will be saved automatically.
          </p>
        </main>
      </RenderGuard>
    );
  }

  const currentStepData = steps[currentStep];

  return (
    <RenderGuard envelope={envelope} proposal={proposal}>
      <main style={PAGE}>
        <h1 style={H1}>Getting started</h1>

        <div style={CARD}>
          <h2 style={H2}>
            Step {currentStep + 1} of {steps.length}: {currentStepData.title}
          </h2>
          <p style={BODY}>{currentStepData.description}</p>
        </div>

        {/* Progress indicator */}
        <div style={CARD}>
          <h2 style={H2}>Your progress</h2>
          <p style={BODY}>
            You are on step {currentStep + 1} of {steps.length}. This guide
            helps you get started with your first lesson.
          </p>
        </div>

        <div style={STACK}>
          <button
            type="button"
            style={PRIMARY_BTN}
            onClick={handleNextStep}
          >
            {currentStepData.action}
          </button>
          <button
            type="button"
            style={SECONDARY_BTN}
            onClick={handleBack}
          >
            {currentStep === 0 ? "Go back" : "Previous step"}
          </button>
          <button
            type="button"
            style={SECONDARY_BTN}
            onClick={handleSignOut}
          >
            Sign out
          </button>
        </div>

        <hr style={DIVIDER} />
        <p style={BODY}>
          You can come back to this guide at any time from your account page.
          The lessons are designed to be completed at your own pace.
        </p>
      </main>
    </RenderGuard>
  );
}