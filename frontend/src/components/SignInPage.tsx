/**
 * Sign-in page (account.signin envelope).
 *
 * Two providers, selected at build time by VITE_AUTH_PROVIDER (ADR 0024):
 *
 *   - "mock"  -> dev/tests; renders an email form. On submit we write
 *                `mock:<email>` to localStorage via setMockToken; the
 *                next API call carries it as Bearer. No round-trip to
 *                the backend is required at submit time — the upsert
 *                happens lazily on the first authenticated request
 *                (whoami fired by App.tsx after onSignedIn).
 *
 *   - "clerk" -> production; renders Clerk's hosted <SignIn /> widget.
 *                Sign-in completion is detected via `useAuth()` inside
 *                a child component (ClerkSignInBranch) so the hook is
 *                only evaluated when ClerkProvider is in the tree.
 *
 * The RenderGuard envelope is intentionally bypassed in the Clerk
 * branch because the rendered tree is a vendor widget we don't own.
 */
import { useEffect, useState } from "react";
import { SignIn, useAuth } from "@clerk/clerk-react";
import { setMockToken } from "../api/auth";
import { loadEnvelope } from "../api/envelope";
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

const AUTH_PROVIDER =
  ((import.meta as unknown as { env?: { VITE_AUTH_PROVIDER?: string } }).env
    ?.VITE_AUTH_PROVIDER ?? "mock");

interface Props {
  onSignedIn: () => void;
  onCancel: () => void;
}

/**
 * Clerk-only sub-component: renders the <SignIn /> widget and watches
 * useAuth() to detect a successful sign-in. When `isSignedIn` flips
 * true (after the user completes Clerk's flow), we call onSignedIn so
 * App.tsx can refresh /auth/whoami and advance the view.
 *
 * Lives inside SignInPage so it can only mount when AUTH_PROVIDER ===
 * "clerk"; otherwise the useAuth() hook would throw for lack of
 * ClerkProvider in the tree.
 */
function ClerkSignInBranch({ onSignedIn, onCancel }: Props) {
  const { isLoaded, isSignedIn } = useAuth();
  useEffect(() => {
    if (isLoaded && isSignedIn) onSignedIn();
  }, [isLoaded, isSignedIn, onSignedIn]);
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
      // it up on the very next request. The account row is upserted
      // lazily by /auth/whoami when App.tsx refreshes after onSignedIn.
      setMockToken(email.trim());
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
              value={email}
              onChange={(ev) => setEmail(ev.target.value)}
              style={FIELD}
              disabled={submitting}
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
            <p style={ALERT_TEXT} role="alert">
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
