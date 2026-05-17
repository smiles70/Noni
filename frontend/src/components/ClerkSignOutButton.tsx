/**
 * ClerkSignOutButton — pure delegator (B6 single sign-out pipeline).
 *
 * Post-AuthProvider cutover this component no longer touches Clerk
 * directly. It renders a styled "Sign out" button that calls the
 * `onSignedOut` callback, which the caller wires to AuthProvider's
 * `signOut()`. AuthProvider then drives the actual provider sign-out
 * (Clerk in clerk mode, mock-token clear in mock mode) and the state
 * transition to SIGNED_OUT.
 *
 * The legacy `useClerk()` dependency is removed: the component now
 * works in both modes and can be renamed `SignOutButton` in a future
 * cleanup once callers update their imports.
 */
import { useState } from "react";
import { SECONDARY_BTN } from "./AccountStyles";

interface Props {
  onSignedOut: () => void | Promise<void>;
  disabled?: boolean;
}

export default function ClerkSignOutButton({ onSignedOut, disabled }: Props) {
  const [submitting, setSubmitting] = useState(false);

  const handleClick = async () => {
    setSubmitting(true);
    try {
      await onSignedOut();
    } catch {
      // Swallow — we still want to leave the account page.
    }
    // No setSubmitting(false): the parent typically unmounts this on
    // the post-signout navigation; setting state on an unmounted
    // component is a React anti-pattern.
  };

  return (
    <button
      type="button"
      style={SECONDARY_BTN}
      onClick={handleClick}
      disabled={submitting || disabled}
    >
      {submitting ? "Signing you out…" : "Sign out"}
    </button>
  );
}
