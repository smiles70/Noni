/**
 * Sign-in page (account.signin envelope).
 *
 * Two providers, selected at build time by VITE_AUTH_PROVIDER (ADR 0024):
 *
 *   - "mock"  -> dev/tests; renders an email form. On submit we write
 *                `mock:<email>` to localStorage via setMockToken and
 *                dispatch `notifyAuthChanged()` so AuthProvider
 *                re-evaluates and transitions AUTHENTICATING -> READY.
 *                Account materialisation happens on AuthProvider's
 *                `/auth/session/init` call, not here.
 *
 *   - "clerk" -> production; renders Clerk's hosted <SignIn /> widget.
 *                Sign-in completion is observed by AuthProvider's
 *                dependency on useClerkAuth().isSignedIn; this page
 *                no longer needs its own onSignedIn callback.
 *
 * The RenderGuard envelope is intentionally bypassed in the Clerk
 * branch because the rendered tree is a vendor widget we don't own.
 */
import { useEffect, useState } from "react";
import { SignIn, useAuth } from "@clerk/clerk-react";
import { setMockToken } from "../api/auth";
import { notifyAuthChanged } from "../auth/AuthProvider";
import { loadEnvelope } from "../api/envelope";
import { AUTH_PROVIDER } from "../lib/env";
import { RenderGuard, type RenderProposal } from "../design/RenderGuard";
import {
  COLORS,
  MOTION,
  RADIUS,
  SPACING,
} from "../design/tokens";
import type { UIStateEnvelope } from "../design/envelope";
import {
  ALERT_TEXT,
  BODY,
  DIVIDER,
  FIELD,
  FIELD_LABEL,
  H1,
  PAGE,
  PRIMARY_BTN,
  SECONDARY_BTN,
  STACK,
} from "./AccountStyles";

// AUTH_PROVIDER imported from lib/env.ts (Sprint 28 quick-win).

interface Props {
  onSignedIn: () => void;
  onCancel: () => void;
}

/**
 * Clerk-only sub-component: renders the <SignIn /> widget.
 *
 * AuthProvider already observes useClerkAuth().isSignedIn and drives
 * the post-signin transition, so this component does NOT invoke
 * onSignedIn from the Clerk hook. The onSignedIn prop remains in the
 * type signature for caller backward-compat but is intentionally
 * unused.
 *
 * Lives inside SignInPage so it only mounts when AUTH_PROVIDER ===
 * "clerk"; otherwise useClerkAuth() would throw for lack of
 * ClerkProvider in the tree.
 */
function ClerkSignInBranch({ onSignedIn: _onSignedIn, onCancel }: Props) {
  // FE Step-4 cutover: AuthProvider now owns the post-signin transition
  // via its dependency on useClerkAuth().isSignedIn. The legacy
  // onSignedIn-from-Clerk callback would race AuthProvider's effect and
  // is intentionally not invoked. The prop remains in the type signature
  // for backward compatibility while callers migrate.
  useAuth();
  return (
    <main style={PAGE} data-component="ClerkSignIn">
      <h1 style={H1}>Sign in</h1>
      {/* routing="virtual" keeps Clerk inside our SPA (no URL changes).
          fallbackRedirectUrl is required by Clerk's API but unused in
          our flow because we drive the post-signin transition
          ourselves via onSignedIn -> App.tsx. */}
      <SignIn routing="virtual" fallbackRedirectUrl="/" />
      <button type="button" style={SECONDARY_BTN} onClick={onCancel}>
        Go back
      </button>
    </main>
  );
}

export default function SignInPage({ onSignedIn, onCancel }: Props) {
  const [envelope, setEnvelope] = useState<UIStateEnvelope | null>(null);
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadEnvelope("account.signin")
      .then(setEnvelope)
      .catch(() => setError("This page is paused. Refresh in a moment."));
  }, []);

  // Clerk path: delegate to a child component so the useAuth() hook
  // is only evaluated when ClerkProvider is in the tree (i.e. when
  // AUTH_PROVIDER === "clerk"). Calling useAuth() in mock mode would
  // crash because the provider is intentionally absent.
  if (AUTH_PROVIDER === "clerk") {
    return <ClerkSignInBranch onSignedIn={onSignedIn} onCancel={onCancel} />;
  }

  if (error) {
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
        <p style={BODY}>One moment — loading.</p>
      </main>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      // Mock provider: persist the bearer token so the apiClient picks
      // it up on the very next request. AuthProvider's resolveSession()
      // will materialise the account row via /auth/session/init.
      setMockToken(email.trim());
      // FE Step-4 cutover: localStorage isn't observable by React, so
      // notify AuthProvider that the credential source changed. This
      // triggers a re-render -> useCredentialSource() re-evaluates ->
      // auth-flow effect transitions AUTHENTICATING -> READY.
      notifyAuthChanged();
      onSignedIn();
    } catch {
      setError("We could not sign you in. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const proposal: RenderProposal = {
    components: ["Heading", "Body", "Button", "Field", "Divider"],
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
    ],
    spacingPxUsed: [SPACING.xs, SPACING.sm, SPACING.md, SPACING.lg, SPACING.xl],
    radiusPxUsed: [RADIUS.sm],
    motionDurationsMs: [MOTION.defaultFadeMs],
    positionShiftPxUsed: [],
    hasUnconfirmedIrreversibleAction: false,
    usesOptimisticProgression: false,
  };

  return (
    <RenderGuard envelope={envelope} proposal={proposal}>
      <main style={PAGE}>
        <h1 style={H1}>Sign in</h1>

        <p style={BODY}>
          Enter the email you would like to use. We will send you a
          one-time link in a moment. There is no password to remember.
        </p>
        <form onSubmit={handleSubmit} style={STACK} aria-busy={submitting}>
          <div>
            <label htmlFor="signin-email" style={FIELD_LABEL}>
              Email
            </label>
            <input
              id="signin-email"
              type="email"
              autoComplete="email"
              required
              minLength={3}
              maxLength={254}
              value={email}
              onChange={(ev) => setEmail(ev.target.value)}
              style={FIELD}
              disabled={submitting}
              aria-invalid={error ? true : undefined}
              aria-describedby={error ? "signin-email-error" : undefined}
            />
          </div>
          <div style={STACK}>
            <button
              type="submit"
              style={PRIMARY_BTN}
              disabled={submitting}
            >
              {submitting ? "Signing you in…" : "Continue"}
            </button>
            <button
              type="button"
              style={SECONDARY_BTN}
              onClick={onCancel}
            >
              Go back
            </button>
          </div>
          {error && (
            <p id="signin-email-error" style={ALERT_TEXT} role="alert">
              {error}
            </p>
          )}
        </form>

        <hr style={DIVIDER} />
        <p style={BODY}>
          Signing in lets us save your progress and remember what works for
          you. You can sign out from your account page at any time.
        </p>
      </main>
    </RenderGuard>
  );
}
