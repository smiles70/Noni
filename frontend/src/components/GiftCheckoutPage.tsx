/**
 * Public gift checkout page.
 *
 * Allows an unauthenticated caregiver to buy mynaani as a gift with just
 * an email address. Per ADR 0021 and the guest-gift checkout intake (P1).
 */
import { useState } from "react";
import { startGuestCheckout } from "../api/billing";
import { COLORS, SPACING } from "../design/tokens";
import { MIN_TOUCH_TARGET } from "../styles/responsiveTokens";
import {
  BODY,
  CARD,
  FIELD,
  FIELD_LABEL,
  H1,
  PAGE,
  PRIMARY_BTN,
  SECONDARY_BTN,
  STACK,
} from "./AccountStyles";
import ChatWidget from "./ChatWidget";

interface Props {
  productCode: string;
  onBack: () => void;
}

export default function GiftCheckoutPage({ productCode, onBack }: Props) {
  const [error, setError] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleBuy = async () => {
    if (!email || !email.includes("@")) {
      setError("Please enter a valid email address.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const res = await startGuestCheckout(productCode, email);
      if (res.checkout_url) {
        window.location.assign(res.checkout_url);
      } else {
        setError("We could not start checkout. Please try again.");
      }
    } catch (err) {
      const detail = (err as { response?: { data?: { envelope_id?: string } } })
        .response?.data?.envelope_id;
      setError(
        detail === "billing.guest_email_required"
          ? "Please enter the email where we should send the gift code."
          : "We could not start checkout. Please try again.",
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main style={PAGE} data-component="GiftCheckoutPage">
      <div style={CARD}>
        <h1 style={H1}>Buy mynaani as a gift</h1>
        <p style={BODY}>
          Give calm, self-paced AI learning to someone you care about. You do
          not need an account. We will send the gift code to your email.
        </p>

        <div style={STACK}>
          <label htmlFor="buyer-email" style={FIELD_LABEL}>
            Your email
          </label>
          <input
            id="buyer-email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            disabled={submitting}
            style={FIELD}
          />
        </div>

        {error && (
          <p
            style={{ ...BODY, color: COLORS.errorConfirm }}
            role="alert"
            aria-live="polite"
          >
            {error}
          </p>
        )}

        <button
          type="button"
          onClick={handleBuy}
          disabled={submitting}
          style={{
            ...PRIMARY_BTN,
            minHeight: MIN_TOUCH_TARGET.mobile,
            marginTop: SPACING.md,
          }}
          aria-busy={submitting}
        >
          {submitting ? "Starting checkout..." : "Continue to payment"}
        </button>

        <button
          type="button"
          onClick={onBack}
          disabled={submitting}
          style={{ ...SECONDARY_BTN, marginTop: SPACING.sm }}
        >
          Go back
        </button>
        <ChatWidget />
      </div>
    </main>
  );
}
