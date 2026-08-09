/**
 * AccountSetupPage - Profile completion form (EPIC-002 Phase 2)
 *
 * Geragogy-compliant account setup page for profile completion.
 * Allows users to add display name and preferences with clear guidance
 * and minimal cognitive load.
 *
 * Key geragogy principles:
 * - Predictable interface with stable layout
 * - Calm, dignified tone without urgency
 * - Clear form labels and instructions
 * - Maximum 3 text levels visible
 * - Maximum 5 primary actionable elements
 * - No irreversible actions without confirmation
 * - Progressive disclosure for complex options
 */
import { useState, useEffect } from "react";
import { apiClient } from "../api/client";
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
  ALERT_TEXT,
  BODY,
  CARD,
  DIVIDER,
  FIELD,
  FIELD_LABEL,
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

interface ProfileData {
  displayName: string;
  preferences: {
    fontSize: "normal" | "large";
    pace: "steady" | "flexible";
  };
}

export default function AccountSetupPage({ onContinue, onBack, onSignOut }: Props) {
  const [envelope, setEnvelope] = useState<UIStateEnvelope | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  const [formData, setFormData] = useState<ProfileData>({
    displayName: "",
    preferences: {
      fontSize: "normal",
      pace: "steady",
    },
  });

  useEffect(() => {
    loadEnvelope("account.setup")
      .then((env) => {
        setEnvelope(env);
        setLoading(false);
        // EPIC-002 Phase 4: Track account setup start
        onboardingTelemetry.trackAccountSetupStart();
      })
      .catch(() => {
        setError("Please wait a moment and refresh the page.");
        setLoading(false);
      });
  }, []); // Empty dependency array is correct - only run on mount

  const handleInputChange = (field: keyof ProfileData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handlePreferenceChange = (pref: keyof ProfileData["preferences"], value: string) => {
    setFormData((prev) => ({
      ...prev,
      preferences: { ...prev.preferences, [pref]: value },
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.displayName.trim()) {
      setError("Please enter your name to continue.");
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      await apiClient.put("/api/v1/account/profile", formData);
      setSuccess(true);
      // EPIC-002 Phase 4: Track account setup completion
      onboardingTelemetry.trackAccountSetupComplete();
      // Auto-continue to getting-started after 2 seconds
      setTimeout(() => {
        onContinue(); // This now goes to getting-started
      }, 2000);
    } catch (err) {
      // EPIC-002 Phase 4: Track error
      onboardingTelemetry.trackError("profile_update_failed", "account_setup");
      setError("Please check your information and try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleSignOut = async () => {
    await onSignOut();
  };

  if (loading) {
    return (
      <main style={PAGE} aria-live="polite" data-component="PendingBanner">
        <p style={BODY}>One moment — loading the account setup page.</p>
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
        <p style={BODY}>One moment — loading the account setup page.</p>
      </main>
    );
  }

  const proposal: RenderProposal = {
    components: ["Heading", "Body", "Button", "Field", "Card", "Divider"],
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
      COLORS.errorConfirm,
      COLORS.accentDesatGreen,
    ],
    spacingPxUsed: [SPACING.xs, SPACING.sm, SPACING.md, SPACING.lg, SPACING.xl],
    radiusPxUsed: [RADIUS.sm, RADIUS.md],
    motionDurationsMs: [MOTION.defaultFadeMs],
    positionShiftPxUsed: [],
    hasUnconfirmedIrreversibleAction: false,
    usesOptimisticProgression: false,
  };

  if (success) {
    return (
      <RenderGuard envelope={envelope} proposal={proposal}>
        <main style={PAGE}>
          <h1 style={H1}>Account setup complete</h1>
          <p style={SUCCESS_TEXT}>
            Your account has been set up successfully. You will be redirected
            to the curriculum in a moment.
          </p>
        </main>
      </RenderGuard>
    );
  }

  return (
    <RenderGuard envelope={envelope} proposal={proposal}>
      <main style={PAGE}>
        <h1 style={H1}>Account setup</h1>

        <p style={BODY}>
          Please provide your name and preferences. This information helps us
          personalize your experience. You can change these settings at any time.
        </p>

        <form onSubmit={handleSubmit} style={STACK} aria-busy={submitting}>
          <div style={CARD}>
            <h2 style={H2}>Your name</h2>
            <div>
              <label htmlFor="display-name" style={FIELD_LABEL}>
                Display name
              </label>
              <input
                id="display-name"
                type="text"
                autoComplete="name"
                required
                minLength={1}
                maxLength={50}
                value={formData.displayName}
                onChange={(e) => handleInputChange("displayName", e.target.value)}
                style={FIELD}
                disabled={submitting}
                aria-invalid={error ? true : undefined}
                aria-describedby={error ? "display-name-error" : undefined}
              />
            </div>
            <p style={BODY}>
              This is the name that will be shown in your account. It can be
              your first name, full name, or a nickname you prefer.
            </p>
          </div>

          <div style={CARD}>
            <h2 style={H2}>Your preferences</h2>
            
            <div>
              <label htmlFor="font-size" style={FIELD_LABEL}>
                Text size
              </label>
              <select
                id="font-size"
                value={formData.preferences.fontSize}
                onChange={(e) => handlePreferenceChange("fontSize", e.target.value)}
                style={FIELD}
                disabled={submitting}
              >
                <option value="normal">Normal size</option>
                <option value="large">Large size</option>
              </select>
            </div>
            <p style={BODY}>
              Choose the text size that is most comfortable for you to read.
            </p>

            <div>
              <label htmlFor="pace" style={FIELD_LABEL}>
                Learning pace
              </label>
              <select
                id="pace"
                value={formData.preferences.pace}
                onChange={(e) => handlePreferenceChange("pace", e.target.value)}
                style={FIELD}
                disabled={submitting}
              >
                <option value="steady">Steady pace</option>
                <option value="flexible">Flexible pace</option>
              </select>
            </div>
            <p style={BODY}>
              Choose how you would like to progress through the lessons.
            </p>
          </div>

          <div style={STACK}>
            <button
              type="submit"
              style={PRIMARY_BTN}
              disabled={submitting}
            >
              {submitting ? "Saving your information…" : "Complete setup"}
            </button>
            <button
              type="button"
              style={SECONDARY_BTN}
              onClick={onBack}
              disabled={submitting}
            >
              Go back
            </button>
            <button
              type="button"
              style={SECONDARY_BTN}
              onClick={handleSignOut}
              disabled={submitting}
            >
              Sign out
            </button>
          </div>

          {error && (
            <p id="display-name-error" style={ALERT_TEXT} role="alert">
              {error}
            </p>
          )}
        </form>

        <hr style={DIVIDER} />
        <p style={BODY}>
          You can change these settings at any time from your account page.
          Your information is stored securely and used only to personalize
          your experience.
        </p>
      </main>
    </RenderGuard>
  );
}