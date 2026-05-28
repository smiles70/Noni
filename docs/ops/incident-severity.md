# Incident Severity Classification

**Version:** 1.0.0
**Owner:** SRE / Platform Engineering
**Last Reviewed:** 2026-05-28

---

## Severity Levels

| Level | Name | Criteria | Response Time | Notification Channel |
|:---|:---|:---|:---:|:---|
| **SEV-1** | Critical | Service completely unavailable; all users affected; data loss possible; security breach confirmed. | Immediate (5 min) | Page on-call -> Eng Lead -> CEO |
| **SEV-2** | Major | Core feature degraded (checkout, auth, curriculum); >25% users affected; no data loss. | 15 minutes | Page on-call -> Eng Lead |
| **SEV-3** | Minor | Non-core feature affected (telemetry export, admin tools); <25% users affected; workaround exists. | 1 hour | Slack #alerts channel |
| **SEV-4** | Informational | Cosmetic issue, performance degradation within SLO, monitoring noise. | Next business day | Ticket for next sprint |

---

## SLO Targets

| Metric | Target | SEV-1/SEV-2 Trigger |
|:---|:---|:---|
| p99 latency | < 500ms | > 500ms for >5 minutes |
| Error rate | < 0.1% | > 1% for >3 minutes |
| Concurrent users | 100 supported | N/A (capacity alert only) |

---

## Escalation Path

```
On-Call Engineer (primary)
    | (no acknowledgment within 5 min OR SEV-1)
Engineering Lead
    | (no acknowledgment within 10 min OR SEV-1)
CEO / Business Lead
    | (security breach OR legal/compliance risk)
Legal / Compliance Officer
```

---

## Classification Examples

| Scenario | Severity |
|:---|:---:|
| All users cannot access the site | SEV-1 |
| Curriculum loads but lessons are blank | SEV-2 |
| Telemetry export is slow but curriculum works | SEV-3 |
| Help center article has a typo | SEV-4 |
| Stripe checkout fails for all users | SEV-1 |
| Gift redemption fails for some users | SEV-2 |
| Landing page image loads slowly | SEV-4 |
| Clerk auth down (users cannot log in) | SEV-1 |
