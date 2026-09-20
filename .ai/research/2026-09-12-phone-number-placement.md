# Research memo — Support phone number placement on the website

**Date:** 2026-09-12
**Related:** intake 013 (`.ai/intake/2026-09-12-phone-number-placement-intake-013.md`)
**Question:** where and how should the toll-free support line
(`1 (877) 409-4144`, answered by the Retell AI receptionist) be
presented on the site — which surfaces, what format, what disclosure?

## Source table (25 sources; 5 independently re-verified via fetch)

| # | URL | Author/Org | Title | Date | Category |
|---|-----|-----------|-------|------|----------|
| 1 | w3.org/WAI/WCAG22/Understanding/target-size-minimum.html | W3C WAI | SC 2.5.8 Target Size (Minimum) | 2023 | WCAG ✅ |
| 2 | w3.org/TR/2023/REC-WCAG22-20231005/ | W3C | WCAG 2.2 Recommendation | 2023 | WCAG |
| 3 | w3.org/WAI/WCAG22/Understanding/link-purpose-in-context | W3C WAI | SC 2.4.4 Link Purpose | 2023 | WCAG |
| 4 | design-system.service.gov.uk/patterns/phone-numbers/ | GOV.UK GDS | Phone numbers pattern | n.d. | Contact design ✅ |
| 5 | design-system.service.gov.uk/patterns/contact-a-department-or-service-team/ | GOV.UK GDS | Contact a service team | n.d. | Contact design |
| 6 | web.dev/articles/click-to-call | Google (web.dev) | Click to Call | 2014 | tel link ✅ |
| 7 | developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/a | MDN | `<a>` element | n.d. | HTML ref |
| 8 | developer.apple.com/library/archive/…/PhoneLinks.html | Apple | Phone Links | n.d. | iOS behavior |
| 9 | datatracker.ietf.org/doc/html/rfc3966 | IETF | RFC 3966 tel URI | 2004 | Standard |
| 10 | nngroup.com/articles/usability-for-senior-citizens/ | NN/g | Usability for Older Adults | 2019 | Senior UX |
| 11 | nngroup.com/articles/usability-seniors-improvements/ | NN/g | Seniors: Improved, Still Lacking | 2013 | Senior UX |
| 12 | nngroup.com/articles/contact-us-pages/ | NN/g | Contact Us Page Guidelines | 2019 | Contact design ✅ |
| 13 | consumer.ftc.gov/consumer-alerts/2025/08/…older-adults | FTC | Impersonators target older adults | 2025 | Anti-scam |
| 14 | consumer.ftc.gov/articles/phone-scams | FTC | Phone Scams | n.d. | Anti-scam |
| 15 | consumer.ftc.gov/consumer-alerts/2024/04/…voice-cloning | FTC | Harmful voice cloning | 2024 | AI trust |
| 16 | ftc.gov/business-guidance/blog/2023/02/keep-your-ai-claims-check | FTC | Keep your AI claims in check | 2023 | AI disclosure |
| 17 | leginfo.legislature.ca.gov/…SB1001 | CA Legislature | SB-1001 Bot disclosure | 2018 | Regulation ✅ |
| 18 | digital-strategy.ec.europa.eu/…article-50-ai-act | EU Commission | AI Act Art. 50 transparency | 2026 | Regulation |
| 19 | aarp.org/pri/…technology-trends-series/ | AARP Research | 2024 Tech Trends 50+ | 2024 | Senior research |
| 20 | pmc.ncbi.nlm.nih.gov/articles/PMC6627975/ | NIA/PMC | Tech to Support Aging in Place | 2019 | Academic |
| 21 | repository.arizona.edu/handle/10150/106378 | U. Arizona/NLM | Senior-Friendly Checklist | 2002 | Senior UX |
| 22 | bentley.edu/…/designing-mobile-experiences-seniors-mind | Bentley U. | Mobile UX for seniors | n.d. | Senior UX |
| 23 | consumer.ftc.gov/consumer-alerts/2025/05/…badge-numbers | FTC | FTC impersonation alert | 2025 | Anti-scam |
| 24 | fcc.gov/spoofing | FCC | Caller ID Spoofing | n.d. | Anti-scam |
| 25 | developers.google.cn/search/blog/2021/07/customer-support | Google | Support methods in Search | 2021 | Contact/SEO |

✅ = re-fetched and content-confirmed this session; remainder verified
live-indexed with matching title/org.

## Key findings (verified claims)

1. **Never hide the phone number.** NN/g: visible contact info builds
   trust; hiding it reads as evasive (12). GOV.UK: order channels by
   user need, show hours/response times (5).
2. **Disclose the AI answerer at or before the call.** CA SB-1001 makes
   bot-nondeception the safe harbor; disclosure must be "clear,
   conspicuous" (17). EU AI Act art. 50: informed at first interaction
   (18). FTC deception doctrine applies (16). The receptionist already
   discloses on pickup; the site copy should set the expectation.
3. **`tel:` link, E.164 format.** RFC 3966 + web.dev: `tel:+18774094144`,
   hyphens for readability (6, 9). iOS confirms before dialing — no
   accidental calls (8). GOV.UK caveat: link styling confuses on
   non-call devices → label it plainly, keep visible text = the number
   itself (4).
4. **Target size:** WCAG 2.5.8 wants 24×24 CSS px; inline-sentence
   targets are excepted but larger is best practice for seniors (1, 22).
5. **Publishing the number is anti-scam armor.** FTC/FCC tell consumers
   to verify a company's real number ON its official website (13, 14,
   23, 24). A published number lets a wary senior verify before dialing —
   and strengthens "we never call you" copy already on HelpPage.
6. **Google will surface the official number** if it's on a findable
   page — reduces wrong-number outcomes (25).
7. **Seniors prefer and often need the phone option** (20, 21); 50+
   adults distrust tech that hides humans (19).

## Decision matrix

| Option | Description | Pros | Cons | Confidence |
|---|---|---|---|---|
| **A. Help page only** | Add to "Contacting support" section on `/help` | Canonical home; covers all personas via nav; smallest surface change | Facility buyers & gift-givers must click through | Medium |
| **B. Help page + journey surfaces (RECOMMENDED)** | Help page canonical block + the same calm contact line on `/gift`, `/for-communities`, `/c/:slug`, `/org` footers | Number present where personas actually transact; facility buyers expect phone contact (12); mirrors chat-widget mount set | Slightly more surface area | **High** |
| C. Site-wide footer | Number on every page incl. learner | Maximum findability | Clutters learner journey; more drift surface; conflicts with calm-contract minimalism | Low |
| D. Chat-only | Keep number unlisted; agents quote it | Zero surface change | Fails FTC-verification use case — the number can't be checked anywhere; NN/g says hiding numbers erodes trust | Low |

**Selected: B.** Help page gets the canonical "Contacting support"
block (email + phone + disclosure). The three facility/community
surfaces and `/gift` carry the identical calm contact line. The learner
curriculum stays clean — `/help` is reachable from learner nav.

## Placement spec (proposed)

- **HelpPage `/help` — "Contacting support" section** gains:
  - `Call us: 1 (877) 409-4144 (toll-free)` as `tel:+18774094144`
    link, number as visible text, `aria-label="Call MyNaani support,
    toll-free"` — meets 2.4.4 purpose-in-context.
  - Disclosure line: "The line is answered by our AI receptionist. It
    can connect you to a person when needed. This call may be stored."
  - Keep email as first-listed channel (email is canonical; phone is
    the talk option).
- **Gift/facility surfaces** get one calm line in their existing footer
  area: `Questions? Call 1 (877) 409-4144 (toll-free) or email
  help@mynaani.com.` — no urgency, no exclamation, matches muted style.
- **Never publish** the staffed transfer number `919-740-4905`.
- Fold in existing copy-drift fixes on HelpPage: `hello@`→`help@` (3×),
  refund window 14→30 days (KB source of truth says 30).

## Edge-case / remediation matrix (top 30)

| # | Trigger | Impact | Mitigation |
|---|---------|--------|------------|
| 1 | `tel:` tap on desktop w/o telephony app | Confusion | GOV.UK pattern: number also readable as text; label says "Call" plainly |
| 2 | iOS auto-detection double-links | Cosmetic | Keep explicit `tel:` link — Safari uses ours; no `format-detection=telephone=no` needed |
| 3 | User fears robot/scam call | Trust | Adjacent AI disclosure + "we never call you" anti-scam line stays |
| 4 | Caller expects a human instantly | UX | Disclosure line sets expectation; transfer path exists |
| 5 | Senior misreads digits | UX | Hyphenated grouping, ≥18px body size, high contrast per tokens |
| 6 | Copy-paste loses digits | UX | Plain-text number remains selectable |
| 7 | Harvesters scrape number | Spam | Toll-free line + AI receptionist absorb it; no extension numbers exposed |
| 8 | Number spoofed by scammers | Trust | Published official number enables verification (FCC/FTC pattern) |
| 9 | Learner sees number mid-lesson | Distraction | Not on curriculum pages; only Help + journey footers |
| 10 | Facility staff dial for billing | Wrong channel | Prompt/agent routes billing to email; copy says "questions" not "billing" |
| 11 | International caller (non-US) | UX | `+1` E.164 in href; toll-free may not be free abroad — disclose "toll-free (US)" |
| 12 | Screen reader announces raw digits | A11y | aria-label spells it out; link purpose in context |
| 13 | Number changes later | Drift | Single constant `SUPPORT_PHONE` in tokens/env-adjacent file; tests assert presence |
| 14 | Page without phone gets stale copy | Drift | Contact copy component or shared constant — one source |
| 15 | "May be stored" scares user | Trust | Mirrors existing disclosure; privacy page already documents it |
| 16 | Geragogy: looks like CTA | Contract | Inline text link, not a button; muted color token |
| 17 | Geragogy: urgency implied | Contract | No "call now," no exclamation, calm wording |
| 18 | `tel:` in email clients | N/A | Not used in emails |
| 19 | Voice assistant (Siri) misreads | Minor | E.164 + hyphens standard; acceptable |
| 20 | User dials off-hours | UX | 24/7 AI receptionist — always answered |
| 21 | Staffed transfer line exposed | Security | Only 877 number published; transfer target stays internal |
| 22 | User wants email instead | UX | Email listed first, phone second |
| 23 | Tests assert old copy | CI | Update HelpPage tests for help@ + 30 days + phone line |
| 24 | KB/site number mismatch | Drift | contact.md + site read same number; add to KB-sync checklist |
| 25 | Chatbot quotes different copy | Consistency | Same disclosure phrasing as begin_message |
| 26 | `tel:` + screen-reader double-announce | Minor | aria-label on link is standard practice |
| 27 | Gift buyer on desktop can't call | UX | Number still copyable; chat widget answers |
| 28 | Regulator asks "was AI disclosed?" | Compliance | Site copy + call start + chat begin all disclose |
| 29 | Footer line crowds facility page | Layout | One line, existing FOOTER style |
| 30 | Persona confusion (gift vs facility) | Boundary | Same number serves both — no persona-specific number needed |

## Codebase conflict check

- `HelpPage.tsx` has `hello@mynaani.com` at 3 sites and a 14-day refund
  line — both conflict with KB canonical (`help@`, 30 days). Fix in the
  same commit.
- No global footer component — each page carries its own FOOTER style;
  the journey-line addition is per-page, low risk.
- Geragogy: `LINK` style + body-size tokens exist; no new tokens needed.
- No learner-page placement → journey-loop-guard unaffected
  (HelpPage is not an entitlement surface; tests still required per
  copy-change convention).

## Gaps / open items

- Owner confirms Option B vs A before implementation.
- Exact disclosure sentence wording — propose: "The line is answered by
  our AI receptionist, who can connect you to a person if needed.
  This call may be stored."
- Structured-data (`Organization.contactPoint`) for Google surfacing —
  optional follow-up (25).
