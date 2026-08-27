# B2B2C-IMPL-001 Implementation Plan

**Process:** v9.51  
**Status:** Pre-flight completed; Phase 1 ready to start.

---

## 1. Architecture trace

### Reuses
- `backend/models/billing.py` — `Product`, `Purchase`, `Entitlement`.
- `backend/services/entitlements.py` — idempotent grant/revoke.
- `backend/api/routes/billing.py` — checkout and webhook patterns.
- `backend/services/payment_provider.py` — `MockPaymentProvider` and `StripePaymentProvider`.
- `frontend/src/components/PaywallPage.tsx` — paywall surface.

### New components
- `backend/models/organizations.py` — `Organization`, `OrgLicense`, `AccessCode`.
- `backend/api/routes/organizations.py` — org staff endpoints.
- `backend/services/org_codes.py` — code generation, validation, redemption.
- `frontend/src/components/OrgCodeEntry.tsx` — paywall code input.

## 2. Data model

```text
Organization
  id: UUID PK
  name: str
  contact_email: str
  admin_email: str
  status: active | inactive

OrgLicense
  id: UUID PK
  org_id: FK
  product_code: FK (modules_4_5)
  total_seats: int
  used_seats: int
  price_cents: int
  purchase_id: FK -> Purchase

AccessCode
  id: UUID PK
  license_id: FK
  code_hash: str (SHA-256 of the user-facing token)
  claimed_by_account_id: FK nullable
  claimed_at: datetime nullable
```

## 3. API endpoints

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/api/billing/org/checkout` | Admin / staff | Create org license and charge |
| POST | `/api/billing/org/{org_id}/codes` | Admin / staff | Generate N access codes |
| POST | `/api/billing/org/redeem` | Learner | Redeem code to own account |
| GET | `/api/billing/org/{org_id}/usage` | Admin / staff | Seats used/remaining |
| GET | `/api/billing/org/{org_id}/codes` | Admin / staff | List codes and claim status |

## 4. Frontend changes

- Add `OrgCodeEntry` to `PaywallPage` as a secondary action.
- On submit, call `POST /api/billing/org/redeem`.
- On success, reload entitlement state and continue.
- On invalid, show plain-language error.

## 5. Security / safety

- Access codes: 32-char URL-safe random tokens.
- Rate-limit `redeem` by IP and account (reuse `RateLimit`).
- Idempotent: same code cannot be claimed twice by different accounts; already-claimed by same account is a no-op.
- Audit: create a `billing_event` for every org redemption.

## 6. Verification

- Backend: `python3 -m compileall backend/`.
- Frontend: `npm run type-check` and `npm run build`.
- Tests: new backend tests for code generation, redeem success, redeem already used, invalid code; frontend test for `OrgCodeEntry`.

## 7. Sequencing

1. Phase 1: Add models and Alembic migration.
2. Phase 2: Add backend endpoints (mock checkout, code generation, redeem).
3. Phase 3: Add paywall code entry.
4. Phase 4: Tests + build + commit.
