/**
 * SignOutButton — pure delegator (B6 single sign-out pipeline).
 *
 * Renders a styled "Sign out" button that calls the `onSignedOut`
 * callback. The caller wires that to AuthProvider's `signOut()`, which
 * clears the mock token and transitions to SIGNED_OUT.
 */
import { useState } from "react";
import { SECONDARY_BTN } from "./AccountStyles";

interface Props {
  onSignedOut: () => void | Promise<void>;
  disabled?: boolean;
}

export default function SignOutButton({ onSignedOut, disabled }: Props) {
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
