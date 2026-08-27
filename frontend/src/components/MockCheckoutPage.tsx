/**
 * Mock checkout page for development and browser previews.
 *
 * In mock mode the payment provider redirects here instead of Stripe.
 * The user can explicitly choose to complete or cancel, then we send
 * them to the same success/cancel URLs the real flow would use.
 */
import { useSearchParams } from "react-router-dom";
import {
  BODY,
  CARD,
  H1,
  H2,
  PAGE,
  PRIMARY_BTN,
  SECONDARY_BTN,
  STACK,
} from "./AccountStyles";

export default function MockCheckoutPage() {
  const [searchParams] = useSearchParams();

  const purchase = searchParams.get("purchase") ?? "";
  const product = searchParams.get("product") ?? "";
  const isGift = searchParams.get("is_gift") === "true";
  const successPath = decodeURIComponent(searchParams.get("success_path") ?? "");
  const cancelPath = decodeURIComponent(searchParams.get("cancel_path") ?? "");
  const giftToken = searchParams.get("gift_token");

  const navigateTo = (path: string) => {
    let url = path;
    if (giftToken) {
      const separator = url.includes("?") ? "&" : "?";
      url = `${url}${separator}gift_token=${encodeURIComponent(giftToken)}`;
    }
    window.location.href = url;
  };

  const price = product === "modules_4_5" ? (isGift ? "$59" : "$39") : "the listed price";

  return (
    <main style={PAGE}>
      <h1 style={H1}>Test checkout</h1>
      <p style={BODY}>
        This is a simulated payment screen for local development. No real
        money is charged.
      </p>

      <section style={CARD}>
        <h2 style={H2}>{isGift ? "Gift purchase" : "Your purchase"}</h2>
        <p style={BODY}>
          Product: <strong>{product}</strong>
        </p>
        <p style={BODY}>
          Purchase ID: <code>{purchase}</code>
        </p>
        <p style={BODY}>
          Amount: <strong>{price}</strong>
        </p>
        {isGift && (
          <p style={BODY}>
            You are buying this for someone else. A gift code will be shown
            after you complete the test payment.
          </p>
        )}
      </section>

      <div style={STACK}>
        <button
          type="button"
          style={PRIMARY_BTN}
          onClick={() => navigateTo(successPath || "/purchase/success")}
        >
          Complete test payment
        </button>
        <button
          type="button"
          style={SECONDARY_BTN}
          onClick={() => navigateTo(cancelPath || "/purchase/cancel")}
        >
          Cancel and go back
        </button>
      </div>
    </main>
  );
}
