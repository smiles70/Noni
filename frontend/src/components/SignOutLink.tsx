/**
 * SignOutLink — landing-surface sign-out button (ADR 0024).
 *
 * Lives on the signed-in landing page so the user can leave without
 * having to drill into Your Account first. Styled to match the landing
 * page's secondary CTA (SECONDARY_BTN from LandingPage's local style
 * set, mirrored here so we don't cross-import).
 *
 * Provider handling mirrors SignInPage's pattern:
 *   - Clerk mode: the inner ClerkBranch uses `useClerk().signOut()`.
 *     The hook is only evaluated when ClerkProvider is in the tree,
 *     which is why this lives in a child component.
 *   - Mock mode: clear the localStorage Bearer and notify the parent.
 *
 * Errors are swallowed (same pattern as ClerkSignOutButton): a transient
 * Clerk failure shouldn't trap the user signed in. The leftover token
 * expires on its own server-side.
 */
import { CSSProperties, useState } from "react";
import { useClerk } from "@clerk/clerk-react";
import { clearMockToken } from "../api/auth";
import {
  COLORS,
  MOTION,
  RADIUS,
  SPACING,
  TYPOGRAPHY,
} from "../design/tokens";

const AUTH_PROVIDER =
  ((import.meta as unknown as { env?: { VITE_AUTH_PROVIDER?: string } }).env
    ?.VITE_AUTH_PROVIDER ?? "mock");

interface Props {
  onSignedOut: () => void | Promise<void>;
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

function ClerkBranch({ onSignedOut }: Props) {
  const clerk = useClerk();
  const [submitting, setSubmitting] = useState(false);
  const onClick = async () => {
    setSubmitting(true);
    try {
      await clerk.signOut();
    } catch {
      /* swallow — let the user out regardless */
    }
    await onSignedOut();
  };
  return (
    <button type="button" style={BTN} onClick={onClick} disabled={submitting}>
      {submitting ? "Signing you out…" : "Sign out"}
    </button>
  );
}

function MockBranch({ onSignedOut }: Props) {
  const [submitting, setSubmitting] = useState(false);
  const onClick = async () => {
    setSubmitting(true);
    clearMockToken();
    await onSignedOut();
  };
  return (
    <button type="button" style={BTN} onClick={onClick} disabled={submitting}>
      {submitting ? "Signing you out…" : "Sign out"}
    </button>
  );
}

export default function SignOutLink(props: Props) {
  return AUTH_PROVIDER === "clerk" ? (
    <ClerkBranch {...props} />
  ) : (
    <MockBranch {...props} />
  );
}
