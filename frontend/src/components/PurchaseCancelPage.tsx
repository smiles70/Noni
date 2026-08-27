/**
 * Purchase cancel page.
 *
 * Shown when a learner leaves a checkout without completing payment.
 * This is also the final stop for the mock "Cancel" button.
 */
import { useNavigate } from "react-router-dom";
import {
  BODY,
  H1,
  PAGE,
  PRIMARY_BTN,
  SECONDARY_BTN,
  STACK,
} from "./AccountStyles";

export default function PurchaseCancelPage() {
  const navigate = useNavigate();

  return (
    <main style={PAGE}>
      <h1 style={H1}>Payment not completed</h1>
      <p style={BODY}>
        You can keep using the free modules for as long as you like, and you can
        choose to purchase again at any time.
      </p>

      <div style={STACK}>
        <button
          type="button"
          style={PRIMARY_BTN}
          onClick={() => navigate("/curriculum")}
        >
          Continue with free modules
        </button>
        <button
          type="button"
          style={SECONDARY_BTN}
          onClick={() => navigate("/paywall")}
        >
          Return to paywall
        </button>
      </div>
    </main>
  );
}
