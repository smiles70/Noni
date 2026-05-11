/**
 * Sign-in page (account.signin envelope).
 *
 * Dev/test mode accepts any email and uses MockAuthProvider via
 * `credential = "mock:<email>"`. Production swaps in Google OAuth
 * (handled outside this component; the page just calls signIn() with
 * whatever credential the OAuth flow produced). See ADR 0023.
 */
import { useEffect, useState } from "react";
import { signIn } from "../api/auth";
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

interface Props {
  onSignedIn: () => void;
  onCancel: () => void;
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
      await signIn(`mock:${email.trim()}`);
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
          Enter the email you would like to use. We will send you a one-time
          link in a moment. There is no password to remember.
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
            <button type="submit" style={PRIMARY_BTN} disabled={submitting}>
              {submitting ? "Signing you in…" : "Continue"}
            </button>
            <button type="button" style={SECONDARY_BTN} onClick={onCancel}>
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
