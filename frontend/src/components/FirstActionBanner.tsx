/**
 * FirstActionBanner - First meaningful action guidance (EPIC-002 Phase 3)
 *
 * Geragogy-compliant banner that encourages users to complete their first
 * meaningful action (starting Module 1) with clear guidance and celebration.
 *
 * Key geragogy principles:
 * - Predictable interface with stable layout
 * - Calm, dignified tone without urgency
 * - Clear guidance without pressure
 * - Maximum 3 text levels visible
 * - Maximum 2 primary actionable elements
 * - Celebrates completion
 * - Respects user pacing
 */
import { useState } from "react";
import {
  COLORS,
  RADIUS,
  SPACING,
} from "../design/tokens";
import {
  BODY,
  PRIMARY_BTN,
  SECONDARY_BTN,
  SUCCESS_TEXT,
  STACK,
} from "./AccountStyles";

interface Props {
  onStart?: () => void;
  onDismiss?: () => void;
  completed?: boolean;
}

export default function FirstActionBanner({ onStart, onDismiss, completed = false }: Props) {
  const [dismissed, setDismissed] = useState(false);

  const handleDismiss = () => {
    setDismissed(true);
    onDismiss?.();
  };

  if (dismissed) {
    return null;
  }

  if (completed) {
    return (
      <div
        style={{
          backgroundColor: COLORS.surface,
          border: `1px solid ${COLORS.accentDesatGreen}`,
          borderRadius: RADIUS.md,
          padding: SPACING.lg,
          marginBottom: SPACING.lg,
        }}
      >
        <h3
          style={{
              marginTop: 0,
            marginBottom: SPACING.sm,
            color: COLORS.textPrimary,
          }}
        >
          Well done
        </h3>
        <p style={SUCCESS_TEXT}>
          You have started your learning journey. Your progress is saved
          automatically. Continue at your own pace.
        </p>
        <div style={STACK}>
          <button
            type="button"
            style={SECONDARY_BTN}
            onClick={handleDismiss}
          >
            Continue learning
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        backgroundColor: COLORS.surface,
        border: `1px solid ${COLORS.accentMutedBlue}`,
        borderRadius: RADIUS.md,
        padding: SPACING.lg,
        marginBottom: SPACING.lg,
      }}
    >
      <h3
        style={{
          marginTop: 0,
          marginBottom: SPACING.sm,
          color: COLORS.textPrimary,
        }}
      >
        Begin your first lesson
      </h3>
      <p style={BODY}>
        Module 1 introduces the basics of AI. This lesson is designed for
        beginners and takes about 30 minutes. Your progress is saved automatically.
      </p>
      <div style={STACK}>
        {onStart && (
          <button
            type="button"
            style={PRIMARY_BTN}
            onClick={onStart}
          >
            Start Module 1
          </button>
        )}
        <button
          type="button"
          style={SECONDARY_BTN}
          onClick={handleDismiss}
        >
          Maybe later
        </button>
      </div>
    </div>
  );
}