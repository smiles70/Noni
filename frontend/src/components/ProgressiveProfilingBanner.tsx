/**
 * ProgressiveProfilingBanner - Gradual preference collection (EPIC-002 Phase 3)
 *
 * Geragogy-compliant banner for progressive profiling that appears during
 * curriculum use to collect additional user preferences gradually.
 *
 * Key geragogy principles:
 * - Predictable interface with stable layout
 * - Calm, dignified tone without urgency
 * - Skippable with clear opt-out
 * - Maximum 3 text levels visible
 * - Maximum 2 primary actionable elements
 * - No irreversible actions
 * - Respects user pacing
 */
import { useState } from "react";
import { apiClient } from "../api/client";
import {
  COLORS,
  RADIUS,
  SPACING,
  TYPOGRAPHY,
} from "../design/tokens";
import {
  BODY,
  CARD,
  PRIMARY_BTN,
  SECONDARY_BTN,
  STACK,
} from "./AccountStyles";

interface Props {
  onDismiss: () => void;
  onComplete: () => void;
}

export default function ProgressiveProfilingBanner({ onDismiss, onComplete }: Props) {
  const [dismissed, setDismissed] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleDismiss = () => {
    setDismissed(true);
    onDismiss();
  };

  const handleCompleteLater = () => {
    // User chooses to complete later
    setDismissed(true);
    onDismiss();
  };

  if (dismissed) {
    return null;
  }

  return (
    <div
      style={{
        backgroundColor: COLORS.surface,
        border: `1px solid ${COLORS.disabled}`,
        borderRadius: RADIUS.md,
        padding: SPACING.lg,
        marginBottom: SPACING.lg,
      }}
    >
      <h3
        style={{
          fontSize: TYPOGRAPHY.headingScale.level3,
          marginTop: 0,
          marginBottom: SPACING.sm,
          color: COLORS.textPrimary,
        }}
      >
        Personalize your experience
      </h3>
      <p style={BODY}>
        We can show you content that better matches how you like to learn.
        This takes about 1 minute and is optional.
      </p>
      <div style={STACK}>
        <button
          type="button"
          style={PRIMARY_BTN}
          onClick={onComplete}
          disabled={submitting}
        >
          Add preferences
        </button>
        <button
          type="button"
          style={SECONDARY_BTN}
          onClick={handleCompleteLater}
          disabled={submitting}
        >
          Maybe later
        </button>
        <button
          type="button"
          style={SECONDARY_BTN}
          onClick={handleDismiss}
          disabled={submitting}
        >
          Dismiss
        </button>
      </div>
    </div>
  );
}