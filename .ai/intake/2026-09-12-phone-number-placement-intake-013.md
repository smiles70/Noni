# Intake 013 — Support phone number placement on the website

**Date:** 2026-09-12
**Status:** problem statement — research protocol running before options
**Requester:** repo owner

## Problem statement

MyNaani now operates a toll-free support line — **1 (877) 409-4144** —
answered by the Retell AI receptionist, which can connect callers to the
staffed line when needed. The number exists today **only inside the
Retell knowledge base** (`retell-mynaani/kb/approved/contact.md`): the
voice agent says it to callers and the website chat agents can quote it.

**The number does not appear anywhere in the site source** — no Help
page entry, no footer, no gift/community page, no privacy/contact copy.
A visitor who has not already engaged a chat agent has no way to find
it, and a caller who wants to verify the number on the website before
dialing (a common trust behavior for older adults wary of phone scams)
cannot do so.

The owner asks: **where and how should the phone number be presented on
the site?** This is a geragogy-affected surface (55+ learners, caregivers,
facility staff) and touches trust, disclosure, and persona boundaries —
so the research protocol must run before any placement decision.

## What is confirmed (fixed inputs)

- The line is toll-free: `1 (877) 409-4144`.
- It is answered by an **AI receptionist**, disclosed as such at call
  start ("I'm MyNaani's AI receptionist… this call may be stored").
- The receptionist can connect callers to the staffed line
  (`919-740-4905`, never published as a dialable number).
- Canonical email `help@mynaani.com` already appears on Help/Privacy and
  stays the primary documented contact path.
- Distinct journeys are in force: learner (B2C), gift-giver, and
  facility/community. Placement may differ per journey.

## Open questions for the research

1. **Which surfaces** should carry the number? Candidates: Help page,
   Privacy/contact block, site footer, `/gift`, `/for-communities`,
   partner/org pages — and whether the learner journey should show it.
2. **Format:** `tel:` click-to-call link, plain text, or both; mobile
   vs desktop behavior; copy-paste friendliness for seniors.
3. **Disclosure wording:** does presenting the number require stating
   "answered by our AI assistant" next to it (CA SB-1001 / EU AI Act
   art. 50 logic, FTC deception concerns)?
4. **Anti-scam framing:** the site already says "we will never call you
   to ask for a password." Does publishing the number change or
   strengthen that copy?
5. **Spam/scraping:** is a plaintext toll-free number on a public site a
   harvesting/robocall-spoofing risk worth mitigating (and how)?
6. **Geragogy:** visual treatment consistent with the calm contract —
   no urgency, no "call now" framing, readable size, no icon-only.

## Constraints

- No changes to the learner curriculum flow; any placement on
  curriculum-adjacent surfaces needs justification.
- No urgency/CTA pressure language (geragogy contract).
- The staffed transfer number is never published.
- No new vendors; `tel:` links and plain copy only.

## Definition of done for the research

- ≥20 verified external sources (accessibility/WCAG, FTC/CA disclosure,
  senior-UX research, anti-spam, support-channel design).
- Decision matrix: footer vs Help page vs per-journey pages vs
  behind-chat-only (≥3 options, confidence levels).
- Top-30 edge cases with mitigations checked against this codebase.
- Recommendation + placement spec ready for implementation + tests.
