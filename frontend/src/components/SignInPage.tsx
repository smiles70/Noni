/**
 * Sign-in page (account.signin envelope).
 *
 * In mock mode, a token of the form `mock:<email>` is stored.
 * In magic mode, the Magic SDK sends a one-time sign-in link and the
 * returned DID token is stored as the Bearer credential.
 *
 * The RenderGuard envelope is used so the page remains subject to the
 * closed-world design contract.
 */
import { useEffect, useState } from "react";
import { setMagicToken, setMockToken } from "../api/auth";
import { notifyAuthChanged } from "../auth/AuthProvider";
import { loadEnvelope } from "../api/envelope";
import { magic } from "../lib/magic";
import { AUTH_PROVIDER } from "../lib/env";
import { RenderGuard, type RenderProposal } from "../design/RenderGuard";
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
import type { UIStateEnvelope } from "../design/envelope";
import {
  COLORS,
  MOTION,
  RADIUS,
  SPACING,
} from "../design/tokens";

interface Props {
  onSignedIn: () => void;
  onCancel: () => void;
}

export default function SignInPage({ onSignedIn, onCancel }: Props) {
  const [envelope, setEnvelope] = useState<UIStateEnvelope | null>(null);
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [magicSent, setMagicSent] = useState(false);

  useEffect(() => {
    loadEnvelope("account.signin")
      .then(setEnvelope)
      .catch(() => setError("Please wait a moment and refresh the page."));
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
        <p style={BODY}>One moment — loading the sign-in page.</p>
      </main>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      if (AUTH_PROVIDER === "magic" && magic) {
        const didToken = await magic.auth.loginWithMagicLink({
          email: email.trim(),
          showUI: false,
        });
        setMagicToken(didToken as string);
        setMagicSent(true);
      } else {
        setMockToken(email.trim());
      }
      notifyAuthChanged();
      onSignedIn();
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Please check your email and try again.";
      setError(message);
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
        {magicSent && (
          <p style={ALERT_TEXT} role="status">
            Please check your email and click the link we sent.
          </p>
        )}
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
