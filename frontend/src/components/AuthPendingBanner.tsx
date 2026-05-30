/**********************************************************************
 * AuthPendingBanner — transient auth-state banner.
 *
 * Shown when AuthProvider reports `state.status === "TRANSIENT_ERROR"`,
 * i.e. the backend cannot currently confirm the session (verifier or DB
 * temporarily unavailable). Per System Constraint Model I-A, signed-in
 * is sticky on transient backend failures: we do NOT log the user out,
 * we surface a non-alarming reconnect indicator instead.
 *
 * Geragogy contract:
 *   - Confidence: "Reconnecting" (not "error", not "failure")
 *   - Reversibility: optional Retry button (no destructive consequence)
 *   - Spatial stability: fixed-height banner; does not shift page content
 *   - Dignity: no jargon, no error code shown
 *
 * Authorized component family: PendingBanner (CONTRACT Section I.D).
 *
 * Tag: login-redesign-v1.
 **********************************************************************/

import { useEffect, useState, type CSSProperties } from "react";
import { COLORS, MOTION, RADIUS, SPACING, TYPOGRAPHY } from "../design/tokens";

interface Props {
  onRetry?: () => void;
}

const BANNER: CSSProperties = {
  backgroundColor: COLORS.surface,
  border: `1px solid ${COLORS.accentMutedAmber}`,
  borderRadius: RADIUS.sm,
  padding: `${SPACING.sm}px ${SPACING.md}px`,
  margin: SPACING.md,
  display: "flex",
  flexDirection: "row",
  alignItems: "center",
  gap: SPACING.md,
  fontFamily: TYPOGRAPHY.fontFamily,
  fontSize: TYPOGRAPHY.bodySizePx,
  lineHeight: TYPOGRAPHY.bodyLineHeight,
  color: COLORS.textPrimary,
  transition: `opacity ${MOTION.defaultFadeMs}ms ease-out`,
};

const TEXT: CSSProperties = {
  margin: 0,
  flex: 1,
};

const RETRY_BTN: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.xs}px ${SPACING.md}px`,
  backgroundColor: COLORS.surface,
  color: COLORS.accentMutedBlue,
  border: `2px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.sm,
  fontWeight: 600,
  cursor: "pointer",
};

const RETRY_AFTER_SECONDS = 15;
const MAX_AUTO_RETRIES = 3;
const RETRY_STORAGE_KEY = "noni.auth_banner_retries";

function getRetryCount(): number {
  try {
    const raw = sessionStorage.getItem(RETRY_STORAGE_KEY);
    return raw ? parseInt(raw, 10) : 0;
  } catch {
    return 0;
  }
}

function incrementRetryCount(): void {
  try {
    const count = getRetryCount() + 1;
    sessionStorage.setItem(RETRY_STORAGE_KEY, String(count));
  } catch {
    /* ignore */
  }
}

export default function AuthPendingBanner({ onRetry }: Props) {
  const [secondsLeft, setSecondsLeft] = useState(RETRY_AFTER_SECONDS);
  const [retryCount, setRetryCount] = useState(getRetryCount);
  const exhausted = retryCount >= MAX_AUTO_RETRIES;

  useEffect(() => {
    if (!onRetry || exhausted) return;
    if (secondsLeft <= 0) {
      incrementRetryCount();
      setRetryCount(getRetryCount());
      onRetry();
      return;
    }
    const t = setInterval(() => {
      setSecondsLeft((s) => s - 1);
    }, 1000);
    return () => clearInterval(t);
  }, [onRetry, secondsLeft, exhausted]);

  return (
    <div role="status" aria-live="polite" style={BANNER}>
      <p style={TEXT}>
        {exhausted
          ? "Still having trouble connecting. Please refresh the page to try again."
          : onRetry
            ? `Reconnecting your sign-in… retrying in ${secondsLeft}s`
            : "Reconnecting your sign-in…"}
      </p>
      {onRetry && !exhausted && (
        <button type="button" onClick={onRetry} style={RETRY_BTN}>
          Try now
        </button>
      )}
    </div>
  );
}
