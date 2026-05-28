# Status Page Plan

**Version:** 1.0.0
**Owner:** SRE

---

## Tool Selection

**Recommended:** [BetterStack](https://betterstack.com) (free tier available)

**Rationale:**
- Already referenced in `.env.example` (`BETTERSTACK_SOURCE_TOKEN`)
- Integrates with existing logging pipeline
- Supports email, SMS, and webhook notifications
- Custom domain support for `status.mynaani.com`

---

## Implementation Steps

1. **Sign up** at betterstack.com
2. **Create status page** with components:
   - Web App (`noni-web.pages.dev`)
   - API Backend (`noni-api.fly.dev/health`)
   - Database (Supabase)
   - Auth (Clerk)
   - Payments (Stripe)
3. **Configure monitors:**
   - HTTP check on `noni-api.fly.dev/health` every 60s
   - HTTP check on `noni-web.pages.dev` every 60s
4. **Add to deploy pipeline:**
   - Update `make deploy-prod` to ping BetterStack "all-clear" after smoke test
5. **Add incident automation:**
   - SEV-1/SEV-2 automatically updates status page
   - All-clear automatically resolves status page

---

## Status Page Content

```markdown
# mynaani Status

## Component Status

| Component | Status |
|:---|:---|
| Web App | Operational |
| API Backend | Operational |
| Curriculum | Operational |
| Checkout | Operational |
| Auth | Operational |

## Incident History

| Date | Duration | Description |
|:---|:---|:---|
| 2026-05-28 | ~2 hours | Frontend deployed with incorrect API base URL. Resolved via rebuild. |

Subscribe to updates: [Email] [RSS]
```

---

## Cost

BetterStack free tier: 10 monitors, 3 status pages, email notifications.
Estimated monthly cost at scale: $29/month (Pro plan for SMS).
