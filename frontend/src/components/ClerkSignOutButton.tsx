/**
 * ClerkSignOutButton — Clerk-aware sign-out trigger (ADR 0024).
 *
 * Why this is its own component:
 *   `useClerk()` requires a surrounding <ClerkProvider>, present only
 *   when VITE_AUTH_PROVIDER === 'clerk'. Putting the hook inside this
 *   small leaf component lets AccountSettingsPage conditionally render
 *   it without ever evaluating the hook in mock mode.
 *
 * Behaviour (Bearer model):
 *   1. `clerk.signOut()` drops Clerk's local session and cookies.
 *      That alone is the entire server-visible sign-out: there is no
 *      backend session to revoke.
 *   2. We then call onSignedOut so App.tsx can refresh /auth/whoami
 *      (which now 401s, no Bearer in flight) and navigate back to
 *      landing.
 *
 * No backend round-trip, no provider-level afterSignOutUrl: navigation
 * is owned by the caller, which avoids the unmount-during-redirect race
 * that would otherwise drop our `await onSignedOut()`.
 *
 * Errors from clerk.signOut() are swallowed deliberately — even an
 * offline/transient failure should free the user from the account page
 * rather than trap them; any leftover Clerk token expires on its own.
 */
import { useState } from "react";
import { useClerk } from "@clerk/clerk-react";
import { SECONDARY_BTN } from "./AccountStyles";

interface Props {
  onSignedOut: () => void | Promise<void>;
  disabled?: boolean;
}

export default function ClerkSignOutButton({ onSignedOut, disabled }: Props) {
  const clerk = useClerk();
  const [submitting, setSubmitting] = useState(false);

  const handleClick = async () => {
    setSubmitting(true);
    try {
      await clerk.signOut();
    } catch {
      // Swallow — we still want to navigate the user out.
    }
    // No `setSubmitting(false)` after onSignedOut: the parent typically
    // unmounts this component on navigation, and setting state on an
    // unmounted component is a React anti-pattern.
    await onSignedOut();
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
