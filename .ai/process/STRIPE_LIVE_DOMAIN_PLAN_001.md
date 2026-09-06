> **Deprecated:** legacy platform retired; production runs on Railway.

# STRIPE-LIVE-001: mynaani.com + Cloudflare + Stripe live plan

**Status:** Pre-flight complete. Awaiting Stripe account and Cloudflare DNS readiness.

---

## 1. Target architecture

```
User -> https://mynaani.com (Cloudflare DNS + CDN)
       |
       |-- / (frontend static bundle)
       |-- /api/* -> backend origin (Railway / legacy-platform)
       |-- /api/billing/stripe-webhook -> backend origin
```

## 2. Cloudflare setup

### DNS records (suggested)

| Type | Name | Target | Proxy |
|------|------|--------|-------|
| A | @ | <backend-or-frontend-IP> | Yes |
| CNAME | www | mynaani.com | Yes |
| CNAME | api | <backend-host> | Yes |

Two options:

### Option A: apex domain to frontend, api subdomain to backend
- `mynaani.com` -> Cloudflare Pages (frontend).
- `api.mynaani.com` -> Railway/legacy-platform backend.
- `FRONTEND_URL=https://mynaani.com`
- `STRIPE_SUCCESS_URL=https://mynaani.com/purchase/success?purchase={purchase_id}`
- `STRIPE_CANCEL_URL=https://mynaani.com/purchase/cancel`

### Option B: all through same origin
- `mynaani.com` -> backend.
- Backend serves static frontend from `frontend/dist/` at root.
- API under `mynaani.com/api/`.
- Simpler for CORS but requires backend to also be a static file server.

## 3. Stripe live checklist

- [ ] Create Stripe account for the mynaani.com business entity.
- [ ] Activate account (bank account, tax info).
- [ ] Create Product "Mynaani Modules 3-5".
- [ ] Create Price for $39 one-time.
- [ ] Create Price for $59 gift one-time.
- [ ] Copy live `STRIPE_SECRET_KEY` and `STRIPE_PUBLISHABLE_KEY`.
- [ ] Create live webhook endpoint `https://api.mynaani.com/api/v1/billing/stripe-webhook`.
- [ ] Select events: `checkout.session.completed`, `charge.refunded`.
- [ ] Copy `STRIPE_WEBHOOK_SECRET`.
- [ ] Set `STRIPE_PRICE_ID_MODULES_4_5` for the $39 price.
- [ ] Decide how to represent the $59 gift (same product, different price, or separate product code).

## 4. Configuration changes

### Backend env

```env
PAYMENT_PROVIDER=stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID_MODULES_4_5=price_...
STRIPE_SUCCESS_URL=https://mynaani.com/purchase/success?purchase={purchase_id}
STRIPE_CANCEL_URL=https://mynaani.com/purchase/cancel
FRONTEND_URL=https://mynaani.com
CORS_ORIGINS=https://mynaani.com,https://www.mynaani.com
```

### Frontend build env

Vite build reads `VITE_API_BASE_URL` or similar? Verify `frontend/src/api/client.ts`.
Update CI to inject `VITE_API_BASE_URL=https://api.mynaani.com` for production builds.

## 5. Verification before launch

- `npm run build` with prod env and `npm run bundle-size`.
- `python -m compileall backend/`.
- Manual Stripe test card: `4242 4242 4242 4242`.
- Refund test: use Stripe test mode if possible, or a small live refund.
- Gift purchase test: buy gift, redeem token with a second account.
- B2B2C code redemption still unlocks Modules 3-5.

## 6. Rollback plan

- Keep `PAYMENT_PROVIDER=mock` branch ready.
- If live fails, switch env back to `mock` and re-deploy.
- Disable Stripe webhooks or switch to test mode endpoint.
