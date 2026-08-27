# Preflight — PRICING-001: Pricing research and selection

**Process:** v9.51  
**Intake:** `.ai/intake/2026-08-27-pricing-research-001.md`

---

## Pre-flight checklist

| # | Gate | Status | Owner | Evidence |
|---|------|--------|-------|----------|
| 1 | Intake approved | GO | Product | Intake file created |
| 2 | Sources available | GO | Research | Web, DOI, AARP, published papers |
| 3 | No code risk | GO | Engineering | Research-only pass |
| 4 | Geragogy guard active | GO | Product | ADR 0021 hard prohibitions apply |
| 5 | Knowledge graph slot reserved | GO | Process | PRICING-001 node added |

## Constraints (binding)

- No subscription / auto-renew / dark-pattern pricing unless a new ADR supersedes ADR 0021.
- Any recommendation must cite verifiable published sources.
- Force-rank must score each model against geragogy, audience WTP, flow, and auth.

## Definitions

- **Older adult / senior:** primary persona is 55+ with limited AI/Claude experience.
- **Flow:** landing hero -> "How it works" -> free account (Magic.link) -> Modules 1-3 -> Module 4 paywall.
- **Auth:** passwordless email (Magic.link) today; caregiver gift requires separate payer account.
