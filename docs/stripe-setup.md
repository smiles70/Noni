# Stripe setup (Sprint B4)

Noni delegates payment to Stripe Checkout. This doc is the exact,
ordered checklist for wiring a Stripe account to a Noni deployment.

You go through it twice:
  - first in **test mode** (no real money; use Stripe's test cards)
  - then with **live keys** once you have at least one staging end-to-end
    success against test mode

## 1. Create the Stripe account / use the existing one

1. Sign in at <https://dashboard.stripe.com>.
2. The dashboard ships with a **Test mode** toggle (top-right). Flip it
   ON for every step below until step 7.

## 2. Create the product and price

1. **Products -> Add product**.
2. Name: `Modules 4 & 5: Building & Composing Claude Skills`.
3. Price model: **One-time**, **USD**, **$49.00**. The recurring/subscription
   options must stay off — Noni's billing flow assumes one-time payment.
4. Save and copy the price ID. It looks like `price_1QABCxxxxxxxxxxxxxxx`.

## 3. Get the API keys

**Developers -> API keys** (test mode):

| Stripe field                  | Noni env var              |
|-------------------------------|---------------------------|
| Secret key (`sk_test_...`)    | `STRIPE_SECRET_KEY`       |
| Publishable key (`pk_test_...`) | `STRIPE_PUBLISHABLE_KEY` |

`STRIPE_PUBLISHABLE_KEY` is only needed if/when we add Stripe Elements
to the frontend. Checkout-only flow does not strictly require it.

## 4. Wire env vars and seed the product row

Add to `.env` (or your secret store):

```env
PAYMENT_PROVIDER=stripe
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_WEBHOOK_SECRET=     # filled in step 5
STRIPE_PRICE_ID_MODULES_4_5=price_1QABCxxxxxxxxxxxxxxx
STRIPE_SUCCESS_URL=http://localhost:5173/purchase/success
STRIPE_CANCEL_URL=http://localhost:5173/purchase/cancel
```

Then seed (or update) the database row that maps `modules_4_5` -> the
Stripe price ID:

```bash
python -m scripts.seed_products
```

The script is idempotent. It prints `created` / `updated` / `unchanged`
so you can run it in deploy pipelines.

## 5. Webhook endpoint + signing secret

The webhook is what tells Noni "the buyer paid" / "the buyer was
refunded". Without it, `POST /api/billing/checkout` returns a checkout
URL but the entitlement never gets granted.

### 5a. Local development (Stripe CLI)

1. Install the Stripe CLI (<https://stripe.com/docs/stripe-cli>).
2. `stripe login` (one-time).
3. Forward events to your local backend:
   ```bash
   stripe listen --forward-to localhost:8000/api/billing/webhook
   ```
4. The CLI prints a `whsec_xxxxx` signing secret. **Copy it into
   `STRIPE_WEBHOOK_SECRET`** and restart the backend.
5. In a second terminal, trigger a test event to confirm wiring:
   ```bash
   stripe trigger checkout.session.completed
   ```
   You should see a 200 from your backend in the `stripe listen` output.

### 5b. Staging / production

1. **Developers -> Webhooks -> Add endpoint**.
2. URL: `https://<your-host>/api/billing/webhook`.
3. Events to send (only these — extras are noise and increase failure
   surface):
   - `checkout.session.completed`
   - `charge.refunded`
4. Save. The dashboard reveals the **Signing secret** (`whsec_xxxxx`).
   Set it as `STRIPE_WEBHOOK_SECRET`.

## 6. End-to-end smoke test (test mode)

1. From a clean browser, sign in, click "Continue paid content".
2. Click "Buy now". You should land on Stripe Checkout.
3. Use card `4242 4242 4242 4242`, any future expiry, any CVC, any ZIP.
4. After Stripe redirects back to `STRIPE_SUCCESS_URL`, refresh the app.
   The paywall should be gone — paid units render normally.
5. To exercise the refund path, find the test payment in the dashboard
   and click **Refund**. Within seconds the paywall should return.

## 7. Going live

1. In the Stripe dashboard, flip **Test mode** OFF.
2. Repeat steps 2-5 with live keys (`sk_live_...`, `whsec_...`).
3. Update env vars in every environment that should accept real
   payments. Staging usually stays on test mode permanently.
4. Re-run `python -m scripts.seed_products` so the live price ID is
   on the row.
5. Smoke-test once with a real charge from a card you control, then
   refund it.

## 8. Failure modes (and what they look like)

| Symptom                                              | Likely cause                                              |
|------------------------------------------------------|-----------------------------------------------------------|
| `/api/billing/checkout` returns 500                  | `STRIPE_PRICE_ID_MODULES_4_5` missing OR product row has stale `stripe_price_id`. Run `seed_products`. |
| Checkout opens but Stripe says "No such price"        | Mismatch between live/test mode — the price ID is from the other mode, or you flipped modes without rotating keys. |
| Buyer pays, redirects back, paywall stays            | Webhook not delivering. Check `stripe listen` output / dashboard's Webhooks -> Events. Most common cause is `STRIPE_WEBHOOK_SECRET` not matching the endpoint Noni is using. |
| Webhook delivered but Noni returns 400               | Signature mismatch. The secret on Noni is for a different endpoint than the one Stripe is calling. |
| Refund processed but entitlement still active        | `charge.refunded` not subscribed at the endpoint, or the purchase row's `stripe_payment_intent_id` was never recorded (check that `checkout.session.completed` fired first). |
