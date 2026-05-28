/**
 * Paywall page (account.paywall envelope).
 *
 * Shown when an authenticated learner reaches paid material without an
 * active entitlement. Three exits, all reversible:
 *   1. Buy for myself        -> Stripe Checkout (self-purchase)
 *   2. Buy as a gift         -> Stripe Checkout (gift; token issued)
 *   3. Redeem a gift token   -> account.gift_redeem
 *
 * Per ADR 0021 the price and product code are backend-driven; we hard-code
 * the product code here only because A4 ships exactly one product. When
 * we add more, this page reads them from the products endpoint.
 */
import { useEffect, useState } from "react";
import { startCheckout } from "../api/billing";
import { loadEnvelope } from "../api/envelope";
import { RenderGuard, type RenderProposal } from "../design/RenderGuard";
import {
  COLORS,
  MOTION,
  RADIUS,
  SPACING,
  TYPOGRAPHY,
} from "../design/tokens";
import type { UIStateEnvelope } from "../design/envelope";
import {
  ALERT_TEXT,
  BODY,
  CARD,
  DIVIDER,
  H1,
  H2,
  PAGE,
  PRIMARY_BTN,
  SECONDARY_BTN,
  STACK,
} from "./AccountStyles";

interface Props {
  productCode: string;
  onRedeemGift: () => void;
  onBack: () => void;
  onHelp?: () => void;
}

export default function PaywallPage({
  productCode,
  onRedeemGift,
  onBack,
  onHelp,
}: Props) {
  const [envelope, setEnvelope] = useState<UIStateEnvelope | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadEnvelope("account.paywall")
      .then(setEnvelope)
      .catch(() => setError("This page is paused. Refresh in a moment."));
  }, []);

  if (error && !envelope) {
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

  const handleCheckout = async (isGift: boolean) => {
    setSubmitting(true);
    setError(null);
    try {
      const { checkout_url } = await startCheckout(productCode, isGift);
      // Server-controlled URL; in prod this is Stripe; in dev it's a mock.
      window.location.href = checkout_url;
    } catch {
      setError("We could not start checkout. Please try again in a moment.");
      setSubmitting(false);
    }
  };

  const proposal: RenderProposal = {
    components: ["Heading", "Body", "Button", "Card", "List", "Divider"],
    primaryActionCount: 3,
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
    spacingPxUsed: [SPACING.sm, SPACING.md, SPACING.lg, SPACING.xl],
    radiusPxUsed: [RADIUS.sm, RADIUS.md],
    motionDurationsMs: [MOTION.defaultFadeMs],
    positionShiftPxUsed: [],
    hasUnconfirmedIrreversibleAction: false,
    usesOptimisticProgression: false,
  };

  return (
    <RenderGuard envelope={envelope} proposal={proposal}>
      <main style={PAGE} aria-busy={submitting}>
        <h1 style={H1}>Continue your learning</h1>
        <p style={BODY}>
          The next modules go a little deeper and require a one-time payment.
          You will keep what you have learned either way; this is your choice.
        </p>

        <section style={CARD}>
          <h2 style={H2}>What you get</h2>
          <ul>
            <li>Modules 4 and 5, with their full set of practice activities.</li>
            <li>
              The same calm, paced pace as the earlier modules — no urgency,
              no time limits.
            </li>
            <li>
              Lifetime access on this account, including any later content
              versions for the same modules.
            </li>
          </ul>
        </section>

        <section style={STACK} aria-label="Choose how to continue">
          <button
            type="button"
            style={PRIMARY_BTN}
            disabled={submitting}
            onClick={() => handleCheckout(false)}
          >
            Continue and purchase for myself
          </button>
          <button
            type="button"
            style={SECONDARY_BTN}
            disabled={submitting}
            onClick={() => handleCheckout(true)}
          >
            Buy as a gift for someone else
          </button>
          <button
            type="button"
            style={SECONDARY_BTN}
            disabled={submitting}
            onClick={onRedeemGift}
          >
            I have a gift code to redeem
          </button>
        </section>

        {error && (
          <p style={ALERT_TEXT} role="alert">
            {error}
          </p>
        )}

        <hr style={DIVIDER} />
        <button
          type="button"
          style={SECONDARY_BTN}
          onClick={onBack}
          disabled={submitting}
        >
          Go back
        </button>

        {onHelp && (
          <p style={{ marginTop: SPACING.md }}>
            <button
              type="button"
              onClick={onHelp}
              style={{
                background: "none",
                border: "none",
                padding: 0,
                color: COLORS.accentMutedBlue,
                textDecoration: "underline",
                cursor: "pointer",
                fontSize: TYPOGRAPHY.bodySizePx,
                fontFamily: TYPOGRAPHY.fontFamily,
              }}
            >
              Questions about buying or gifting
            </button>
          </p>
        )}
      </main>
    </RenderGuard>
  );
}
