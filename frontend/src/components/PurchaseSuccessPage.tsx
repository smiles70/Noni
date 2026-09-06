/**
 * Purchase success page.
 *
 * Works for both real (Stripe) and mock checkout. In mock mode it also
 * calls the backend to mark the purchase as paid and grant the
 * entitlement.
 */
import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { mockCheckoutComplete } from "../api/billing";
import {
  ALERT_TEXT,
  BODY,
  CARD,
  H1,
  H2,
  PAGE,
  PRIMARY_BTN,
  SECONDARY_BTN,
  STACK,
  SUCCESS_TEXT,
} from "./AccountStyles";

export default function PurchaseSuccessPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const purchase = searchParams.get("purchase") ?? "";
  const product = searchParams.get("product") ?? "";
  const provider = searchParams.get("provider") ?? "";
  const isGift = searchParams.get("is_gift") === "true";
  const giftToken = searchParams.get("gift_token");

  const [loading, setLoading] = useState(provider === "mock" && !isGift);
  const [error, setError] = useState<string | null>(null);
  const [completed, setCompleted] = useState(false);
  const giftCode = giftToken;

  useEffect(() => {
    if (provider !== "mock" || isGift) {
      // Real Stripe completion is handled by webhooks; gift token is
      // already known.
      setLoading(false);
      return;
    }
    if (!purchase) {
      setLoading(false);
      return;
    }
    mockCheckoutComplete(purchase)
      .then((res) => {
        if (res.granted) {
          setCompleted(true);
        } else {
          setError("We could not activate your access. Please try again.");
        }
        setLoading(false);
      })
      .catch(() => {
        setError("Something went wrong while completing the test payment.");
        setLoading(false);
      });
  }, [purchase, provider, isGift]);

  return (
    <main style={PAGE} aria-busy={loading}>
      <h1 style={H1}>
        {isGift ? "Gift purchase complete" : "Purchase complete"}
      </h1>

      {loading && (
        <p style={BODY} aria-live="polite">
          One moment — confirming your payment.
        </p>
      )}

      {!loading && error && (
        <p style={ALERT_TEXT} role="alert">
          {error}
        </p>
      )}

      {!loading && !error && (
        <>
          {isGift ? (
            <section style={CARD}>
              <h2 style={H2}>Give this code to the learner</h2>
              <p style={BODY}>
                They can use the "I have a gift code to redeem" option on the
                paywall to activate their access.
              </p>
              <p style={SUCCESS_TEXT}>
                Gift code: <code>{giftCode ?? "—"}</code>
              </p>
            </section>
          ) : (
            <section style={CARD}>
              <h2 style={H2}>You now have lifetime access</h2>
              <p style={BODY}>
                Product: <strong>{product}</strong>
              </p>
              {completed && (
                <p style={SUCCESS_TEXT}>
                  Your access has been activated. You can continue to the next
                  module whenever you are ready.
                </p>
              )}
            </section>
          )}

          <section style={CARD}>
            <h2 style={H2}>What happens next</h2>
            <p style={BODY}>
              Your access is permanent — there is no subscription and no
              further charge. You can continue now, or come back any time;
              your progress is saved. If you ever need help, the "Help and
              common questions" page explains how to reach us.
            </p>
          </section>

          <div style={STACK}>
            <button
              type="button"
              style={PRIMARY_BTN}
              onClick={() => navigate("/curriculum")}
            >
              Continue to the curriculum
            </button>
            <button
              type="button"
              style={SECONDARY_BTN}
              onClick={() => navigate("/paywall")}
            >
              Go back
            </button>
          </div>
        </>
      )}
    </main>
  );
}
