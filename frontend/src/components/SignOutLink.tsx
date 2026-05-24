/**
 * SignOutLink — landing-surface sign-out button (ADR 0024 / B6).
 *
 * Pure delegator: this component owns no provider knowledge, no
 * credential reads, and no `useClerk()` call. It triggers sign-out
 * exclusively via AuthProvider's `signOut()` (B6 single sign-out
 * routine), which in turn drives the Clerk SDK in clerk mode and
 * clears the mock token in mock mode.
 *
 * Errors are swallowed (matches ClerkSignOutButton): a transient
 * provider failure shouldn't trap the user signed in. The leftover
 * server-side token expires on its own.
 *
 * The `onSignedOut` prop is retained for LandingPage back-compat: the
 * parent passes `signOut` itself, which is redundant but harmless
 * (AuthProvider.signOut is idempotent). A follow-up cleanup can drop
 * the prop and stop threading it from App.tsx → LandingPage.
 */
import { CSSProperties, useState } from "react";
import { useAuth } from "../auth/AuthProvider";
import {
  COLORS,
  MOTION,
  RADIUS,
  SPACING,
  TYPOGRAPHY,
} from "../design/tokens";

interface Props {
  /** Optional hook for the parent (LandingPage back-compat). Fires
   *  after AuthProvider.signOut() resolves. */
  onSignedOut?: () => void | Promise<void>;
}

const BTN: CSSProperties = {
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

export default function SignOutLink({ onSignedOut }: Props) {
  const { signOut } = useAuth();
  const [submitting, setSubmitting] = useState(false);

  const handleClick = async () => {
    if (submitting) return;
    setSubmitting(true);
    try {
      await signOut();
      if (onSignedOut) await onSignedOut();
    } catch {
      // swallow intentionally — let the user out regardless
    }
    // Do not reset submitting: this component typically unmounts after
    // the post-signout state transition; setState on an unmounted
    // component is a React anti-pattern (matches ClerkSignOutButton).
  };

  return (
    <button
      type="button"
      style={BTN}
      onClick={handleClick}
      disabled={submitting}
    >
      {submitting ? "Signing you out…" : "Sign out"}
    </button>
  );
}
