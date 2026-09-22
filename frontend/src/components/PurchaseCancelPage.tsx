/**
 * Purchase cancel page.
 *
 * Shown when a learner leaves a checkout without completing payment.
 * This is also the final stop for the mock "Cancel" button.
 * Shared surface: learner self-purchase and caregiver gift checkout.
 * PS-BID17-032: paywall CTA suppressed when the user already holds an
 * entitlement — an entitled learner must never be routed back to the
 * paywall (journey-loop guard).
 */
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { loadPaidUnit } from "../api/curriculum";
import { MARKETING, SPACING } from "../design/tokens";
import {
  BODY,
  CARD,
  H1,
  PRIMARY_BTN,
  SECONDARY_BTN,
  STACK,
} from "./AccountStyles";

const PAGE: React.CSSProperties = {
  minHeight: "100vh",
  backgroundColor: MARKETING.paper,
  paddingTop: SPACING.xl,
};

export default function PurchaseCancelPage() {
  const navigate = useNavigate();
  const [entitled, setEntitled] = useState<boolean | null>(null);

  useEffect(() => {
    let cancelled = false;
    loadPaidUnit(3, "module3-unit-1")
      .then((r) => {
        if (!cancelled) setEntitled(r.kind !== "paywall");
      })
      .catch(() => {
        if (!cancelled) setEntitled(null);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main style={PAGE}>
      <div style={CARD}>
        <h1 style={H1}>Payment not completed</h1>
        <p style={BODY}>
          You can keep using the free modules for as long as you like, and you
          can choose to purchase again at any time.
        </p>

        <div style={STACK}>
          {entitled ? (
            <button
              type="button"
              style={PRIMARY_BTN}
              onClick={() => navigate("/paid-curriculum")}
            >
              Continue to the paid modules
            </button>
          ) : (
            <button
              type="button"
              style={PRIMARY_BTN}
              onClick={() => navigate("/curriculum")}
            >
              Continue with free modules
            </button>
          )}
          {!entitled && (
            <button
              type="button"
              style={SECONDARY_BTN}
              onClick={() => navigate("/paywall")}
            >
              Return to paywall
            </button>
          )}
        </div>
      </div>
    </main>
  );
}
