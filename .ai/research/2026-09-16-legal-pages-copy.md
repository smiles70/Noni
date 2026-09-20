# Research — Terms of Service + Privacy content (plain-language legal)

**Date:** 2026-09-16
**Intakes:** `.ai/intake/2026-09-16-p2-landing-mini-footer.md`,
`.ai/intake/2026-09-16-p2-marketing-fat-footer.md`
**Question:** What must `/terms` and `/privacy` contain, and in what
register, for a consumer product aimed at adults 55+?

## Sources

### ToS clause requirements

| # | Source | Key finding |
|---|---|---|
| 1 | ISO 21800:2025 (iso.org/standard/86883) | International guidance for clear, accessible, fair B2C online T&Cs — the authoritative baseline for our register. |
| 2 | TermsBox 12-area ToS checklist (termsbox.com/blog/tos-template) | Required areas: acceptance, eligibility, account, service description, fees/billing, acceptable use, user content, IP, third-party services, disclaimers/LoL, indemnification, termination/law/changes/contact. |
| 3 | Sprintlaw mobile-app ToS checklist | Active acceptance preferred; eligibility (13+ COPPA floor), payment terms, termination, dispute resolution, changes notice. |
| 4 | TermsFeed clauses guide (termsfeed.com) | Introduction/acceptance, reference to privacy policy, authorized users, user submissions — plus consent display mechanics. |
| 5 | UDT "How to write ToS" (ultimatedesigntools.com) | Five functions: limit liability, disclaim warranties, dispute rules, protect IP, define permitted use. Notes CA/EU auto-renewal disclosure (n/a — we sell one-time access, not subscriptions). |

### Plain-language legal writing

| # | Source | Key finding |
|---|---|---|
| 6 | UK BEIS/CMA evidence report (publishing.service.gov.uk PDF) | Q&A format improved consumer understanding **36%**; summaries + explanatory icons +34%. Reading-age scores do NOT predict comprehension — structure does. |
| 7 | ISO 24495-2 (draft) Plain language — legal communication | Plain legal language preserves legal effect; readers must be able to find, understand, and exercise rights. |
| 8 | STET/Editorially ToS case study (stet.editorially.com) | Readable ToS is achievable without weakening obligations; short sentences, numbered/bulleted lists, no legalese for its own sake. |
| 9 | Luxembourg plain-language banking guide (public.lu) | Target ≤B2 vocabulary; sans-serif 12–14pt; no italics/underlines except links; bold for emphasis only. |
| 10 | NIA/NLM senior-friendly checklist (from parent memo) | Consistent structure, explicit step-by-step procedures, positive statements, careful labels — our existing PrivacyPage already follows this. |

### Privacy-policy required contents

| # | Source | Key finding |
|---|---|---|
| 11 | CCPA §7011(e) verbatim (verified fetch) | Required contents: PI categories (CCPA taxonomy), sources, purposes, sale/share disclosure, retention, consumer rights (know/delete/correct/opt-out/non-discrimination), how to exercise, opt-out preference signals, authorized agent, contact, last-updated date. |
| 12 | CPPA §7003(c) conspicuous-link rules | Link text uses the word "privacy"; comparable prominence to other links. |
| 13 | FTC Fair Information Practices + .com Disclosures | Clear-and-conspicuous notice; plain language; proximity to collection. |
| 14 | GDPR Art. 12 (transparent communication) | Concise, transparent, intelligible, easily accessible, clear and plain language. |

## Site scan — facts the copy must cover

- **Auth:** Magic.link email links — we collect email only.
- **Payments:** Stripe checkout (PCI L1); we never see card numbers.
  One-time purchase unlocks Modules 2–5 — **not a subscription**;
  no auto-renewal clause needed (avoid implying one).
- **Gifts:** gift tokens, delivered by email/print, redeemed on
  account; refund to purchaser.
- **Refunds:** 30 days, full refund, asked to have completed <50% of
  paid modules ("keeps the promise fair").
- **Deletion:** scheduled 30 days out, cancelable; then permanent.
- **Data:** email, lesson progress, access code (if org/gift).
  No contacts/photos/location/tracking.
- **Processors:** Stripe, Magic.link, Railway, Cloudflare, Retell AI
  (phone/chat on gift & community pages; transcripts PII-scrubbed,
  30-day retention). No ad networks, no data brokers.
- **Org boundary:** facility staff see whether a code was used —
  never lessons/answers/activity.
- **Audience:** adults 55+ — not directed at children; state 18+
  (or capacity-to-contract) eligibility plainly.

## Copy decisions

1. **Register:** match PrivacyPage's proven voice — plain sentences,
   "you/we", sectioned questions-as-headings where natural (BEIS:
   Q&A format +36% comprehension). Short sections, no walls.
2. **TermsPage sections** (mapped to the 12-area checklist):
   - What you're agreeing to (acceptance; "using mynaani means…")
   - Who can use mynaani (18+/capacity; accurate email)
   - Your account (magic-link sign-in; keep email current)
   - What mynaani is (AI learning curriculum; we may improve/change
     content — service description)
   - Paying (one-time access to Modules 2–5; Stripe; taxes)
   - Refunds (30-day, <50% rule, gifts→purchaser)
   - Gifts (tokens, delivery, redemption, non-transferability note)
   - Community programs (access codes; org sees code use only —
     cross-ref privacy)
   - Fair use (no scraping/reselling/account sharing; one learner
     per account)
   - Ownership (our content is ours; your progress data is yours)
   - What we don't promise (educational content, not professional
     advice; service provided as-is — disclaimer, plainly)
   - If something goes wrong (contact; liability cap in plain terms;
     governing law — Delaware? flag: needs legal-entity facts)
   - Ending your account (deletion flow; we may suspend for misuse)
   - Changes to these terms (notice on this page; continued use =
     acceptance)
   - Contact (help@mynaani.com — wait, user said no email in
     *footer*; a contact inside the terms page body is standard and
     already used on Privacy/Help pages — keep it there, not in
     footer)
3. **PrivacyPage — enhance, don't rewrite.** Existing page covers
   collection/processors/deletion well in our voice. Add a closing
   section "Your rights under privacy law" covering: last-updated
   date, rights list (know/delete/correct/non-discrimination), how to
   exercise (account page + help@), no sale/share (already stated —
   formalize), Global Privacy Control honored statement, authorized
   agent note. Keeps plain voice; satisfies §7011(e) checklist items
   that are currently implied but not explicit.

## Flags needing user/legal confirmation

- **Legal entity name + governing state** — terms need "operated by
  [entity]" and a governing-law clause. Placeholder: `mynaani` +
  Delaware pending confirmation.
- Whether B2B/community contracts need separate terms (out of scope —
  covered by partner agreements).
