# Research: Attaching signed-in learner identity to the help-callback contact

**Date:** 2026-09-18
**Ticket:** smiles70/Noni#71 — Help callback should identify the signed-in
learner (email from magic-link session)
**Intake:** `.ai/intake/2026-09-18-learner-help-channel.md`

## Research question

How should a support-callback request carry the authenticated learner's
identity (session email) into CRM contact filing so ops sees *who* asked for
help — without creating duplicate contacts or leaking PII to third parties?

## Verified sources (21)

### Engineering / vendor docs (7)

1. PostHog — Identity resolution docs. Identity is the app's job; mint a
   stable ID early, link explicitly at transitions; unlinked anonymous→auth
   splits produce duplicate persons. *(webfetch-verified)*
   https://posthog.com/docs/product-analytics/identity-resolution
2. Twilio Segment — Spec: Identify (userId vs anonymousId; traits carry
   email/name once known). https://www.twilio.com/docs/segment/connections/spec/identify
3. Twilio Segment — Working with IDs (userId is canonical, highest fidelity).
   https://www.twilio.com/docs/segment/guides/working-with-ids
4. Twilio Segment — Best practices: Identify (link anonymousId on auth).
   https://www.twilio.com/docs/segment/connections/spec/best-practices-identify
5. Twilio Segment — ExternalIDs / identity resolution (email promoted to
   externalID; same externalID merges profiles).
   https://www.twilio.com/docs/segment/unify/identity-resolution/externalids
6. GraphJSON — Identity stitching & account lifecycle (opaque IDs; emit a
   link fact at sign-in; keep PII out of user_id).
   https://www.graphjson.com/docs/Guides/identity-stitching-and-account-lifecycle
7. Salesforce Data Cloud identity resolution (via CRM Curator) — deterministic
   matching first (normalized email, E.164 phone); probabilistic only with
   confidence scores. https://crmcurator.com/articles/salesforce/identity-resolution-rulesets/

### Academic (5)

8. Fellegi & Sunter (1969), *A Theory for Record Linkage*, JASA.
   DOI 10.1080/01621459.1969.10501049 — formal link/non-link/possible-link
   decision framework; false-positive cost is an explicit input.
9. Fellegi-Sunter canonical PDF (Cornell course mirror).
   https://www.cs.cornell.edu/~shmat/courses/cs6434/fellegi-sunter.pdf
10. Winkler (2000), *Using the EM Algorithm for Weight Computation in the
    Fellegi-Sunter Model*, US Census Bureau RR2000-05.
    https://www.census.gov/content/dam/Census/library/working-papers/2000/adrm/rr2000-05.pdf
11. Di Biase et al. (2020), *An Improved Fellegi-Sunter Framework*, Journal of
    Official Statistics. DOI 10.2478/jos-2020-0039 — blocking reduces the
    comparison space at the cost of unseen true matches.
12. Benjelloun et al. (2009), *Swoosh: a generic approach to entity
    resolution*, VLDB Journal. DOI 10.1007/s00778-008-0098-x — merge/dedup
    semantics for records accumulated from multiple sources.

### Industry / ops / security (6)

13. OWASP — Webhook Security Guidelines Cheat Sheet: don't log full payloads
    (PII), per-webhook secrets, idempotent processing, event-ID dedup.
    *(webfetch-verified)*
    https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets_draft/Webhook_Security_Guidelines_Cheat_Sheet.md
14. OWASP API10:2023 — Unsafe API Consumption: third-party payloads can carry
    PII into logs; validate, isolate, minimize.
    https://ammune.ai/blog/owasp-api10-2023-unsafe-api-consumption
15. GDPR Art. 5(1)(c)/(e) analysis — data minimisation & storage limitation
    applied to webhook payload storage. https://instawebhook.com/blog/webhooks-and-gdpr-managing-personally-identifiable-information-in-payloads
16. APIMart — API logging for compliance: log opaque IDs, keep identity
    mapping separately; GDPR minimisation vs SOC 2 audit trail.
    https://apimart.ai/blog/ultimate-api-logging-compliance-guide
17. NIST SP 800-122, *Guide to Protecting the Confidentiality of PII* —
    minimisation: collect/forward only what the purpose requires.
18. gethook.to — GDPR webhook retention: prefer bounded retention and
    minimal payload fields. https://gethook.to/blog/gdpr-webhook-data-retention

### Practitioner / discussion (3)

19. TaggingDocs — sGTM user stitching (write identity map at login; backfill
    only via explicit pair lookup). https://taggingdocs.com/server-side/advanced/user-stitching/
20. GA4 user backstitching — post-hoc resolution is possible but lossy;
    event-time identity beats backstitching.
    https://adriennevermorel.com/notes/ga4-user-backstitching/
21. Routine / Icypeas / MapsLeads dedup guides — match-key hierarchy:
    normalized email first, E.164 phone second, name+context last;
    deterministic rules before fuzzy. (representative practitioner consensus)
    https://routine.co/blog/posts/deduplicate-crm-ai-fuzzy-merge
    https://www.icypeas.com/blog/merge-duplicate-contacts
    https://www.mapsleads.co/blog/crm-deduplication-best-practices

## Decision matrix

| Alternative | How | Pros | Cons | Verdict |
| --- | --- | --- | --- | --- |
| A. Pass email in Retell `metadata` | Noni adds `metadata.email` to create-phone-call; webhook stamps contact | One write path; alert sees email immediately | Sends PII to a third-party telephony vendor for no call purpose (GDPR 5(1)(c), NIST 800-122, OWASP API10); metadata surfaces in Retell dashboards/logs | Rejected |
| B. Attach email via the CRM `form_submit` event (existing path) | Noni already sends `fields.email` from the session; CRM tracking filing writes email+phone on the same contact | PII stays inside our systems; uses existing first-party intake; deterministic keys (email → phone) | Two writes (tracking event + Retell webhook) must converge on one contact | **Chosen** |
| C. Agent-side backfill task | Periodic job joins phone-keyed Retell contacts to email-keyed tracking contacts | No intake changes | Delayed identity in alerts; merge jobs are the highest-risk operation in dedup (orphans activities); backstitching is lossy (#20) | Rejected |

**Confidence: high.** Consensus across PostHog, Segment, Salesforce, and the
academic lineage is: deterministic identifiers first, attach identity at the
earliest authoritative point (the authenticated session), keep PII out of
third parties, prefer link-at-source over merge-later.

## Codebase conflict check

- `backend/services/retell_calls.py:65` — `file_help_contact` **already sends
  `fields.email`** when the session has one. No Noni diff needed.
- `frontend/src/api/help.ts:20` — already sends `credentials: "include"`.
- `backend/api/routes/help.py:32-57` — `get_optional_account` already resolves
  the session account and passes `account.email`.
- `apps/api/src/tracking/tracking-ingest.service.ts` — extracts `email` and
  `name` from fields; **drops `fields.phone`** — the real gap.
- `apps/api/src/tracking/tracking-filing.service.ts:69,110` — `file()` matches
  `findFirst({email})` and creates `{email, firstName, lastName}` — **no
  `phone`**, so the later Retell webhook (identity = phone) cannot match the
  email-keyed contact → creates a second, phone-only contact. Duplicate
  person = the exact failure mode in PostHog doc + ticket.
- `apps/api/src/retell/retell.service.ts:160-184` — `findOrCreate` matches
  `OR [email, phone]` and updates `phone`/`name` on match; once the tracking
  contact carries `phone`, both write paths converge on one record.
- Constraint: `contact.firstName` is non-null; phone-keyed creates must keep
  a safe default (retell path uses "Caller").

## Edge-case / remediation matrix (top 30 — callback scope)

| # | Case | Handling |
| --- | --- | --- |
| 1 | Signed-in learner, email+phone in fields | file() writes email+phone; Retell webhook matches by phone → one contact |
| 2 | Unsigned-in learner, phone only | form_submit still skips (crm#3); Retell webhook files phone-only — alert shows number only |
| 3 | Retell webhook lands BEFORE the form_submit | webhook creates phone-only contact; form_submit then finds it — needs phone-aware attach (below) |
| 4 | form_submit lands first | contact has email+phone; webhook matches by phone → same contact |
| 5 | Two learners share a phone (household) | **never match a new email to a contact that already has a different email** — attach phone only when existing contact has no email, or when email matches |
| 6 | Phone already on a DIFFERENT contact with email | keep separate contacts; log the conflict, don't merge |
| 7 | Email exists on one contact, phone on another | prefer the email match; do not auto-merge (Fellegi-Sunter: false-positive cost is explicit) |
| 8 | Malformed phone in fields | normalizePhone-style sanitisation at ingest; drop if not E.164-able |
| 9 | Phone field contains non-digits/letters | strip to digits; require 10-11 digits US/CA |
| 10 | Duplicate form_submit (double-tap) | same keys → attach to same contact; idempotent by contact match |
| 11 | Machine/automated email | existing isMachineAddress/isAutomatedAddress skips stay first |
| 12 | Workspace-domain email (staff testing) | existing workspaceDomains skip stays |
| 13 | Suppressed email/domain | existing suppression check stays before any create |
| 14 | Contact cap hit | existing counters.take() + release-on-race stays |
| 15 | Phone present but empty string | treat as absent |
| 16 | fields has `tel`, `mobile`, `number` variants | ingest picks all phone-ish keys |
| 17 | Retell `to_number` vs learner number | keep existing to_number logic — unrelated to this change |
| 18 | Email changes after contact exists | not handled here (contact update is a separate policy) |
| 19 | Session cookie missing → account null | `fields.email` absent; degrade to phone-only (case 2) |
| 20 | Session expired mid-request | same as 19 |
| 21 | CRM tracking ingest drops unknown field names | add `phone` extraction alongside existing `nameFrom`/`email` picks |
| 22 | Contact created without name from email+phone event | splitName() already derives firstName from email local-part |
| 23 | Alert text for identified learner | notifier already prints email/phone from contact — no change needed |
| 24 | Phone normalisation mismatch (202 vs +1202) | normalise at BOTH ingest and match (strip +1) — key consistency |
| 25 | Rate-limited callback (4th call) | form_submit still files → alert records the request even without a call |
| 26 | Retell call fails entirely | form_submit with email still files → ops can call manually |
| 27 | fields.email present but not on account record | only session-derived email is sent; no learner-supplied email field exists — no spoofing surface |
| 28 | Replay/duplicate Retell events | existing advisory lock + OR-match keep one contact |
| 29 | Archived contact with same email | findFirst uses archivedAt:null — archived records don't match; new contact created |
| 30 | PII in logs | log contactId + event type only; never log email/phone values (OWASP §13) |

## Recommended approach (B)

1. **Ingest** (`tracking-ingest.service.ts`): extract `phone` from form
   fields with the same `pick()` pattern (phone/tel/mobile/number keys and
   a digit-normalised fallback) → include in the submission handed to `file()`.
2. **File** (`tracking-filing.service.ts`):
   - match `findFirst({ OR: [{email}, {phone}] })` **only when** the phone
     match target has no email (phone-only contact may upgrade); never attach
     a new email to a contact that already carries a different email.
   - create with `phone` when present.
   - on attach to an existing contact, stamp `phone` if the contact lacks it.
3. **No Noni changes** — the session email already flows.
4. **No PII to Retell** — metadata stays phone-only by design.
5. Tests: ingest picks phone keys; file() converges tracking+webhook into one
   contact; household-shared-phone does not merge two emails.
