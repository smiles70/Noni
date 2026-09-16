# Intake — Footer/contact follow-up items

**Date:** 2026-09-16  
**Status:** in_progress  
**Source:** User-directed follow-up after successful staging UAT of
footer/legal pages.  
**Tickets:**  
1. Sage green background for the fat footer.  
2. Email-client button vs. inline form — research.  
3. Partner contact form (mimic GetSetUp).  
4. Social media links (Instagram, TikTok, YouTube).

---

## Ticket 1 — Sage green footer background

### Description
Apply Mynaani's sage/desaturated green color as the background of the
shared `Footer.tsx` ("fat footer") on `/caregiver` and `/for-communities`.

### Acceptance criteria
- Footer background uses the existing `accentDesatGreen` token (`#4A6D5C`).
- Footer text/links maintain WCAG 2.1 AA contrast.
- Fixed hero stays fixed; only the scrollable marketing pages change.
- Render-guard `colorsUsed` updated and passes.

### Geragogy / contract notes
- `accentDesatGreen` currently is approved only for success/confirmations
  per the V1 color contract. Using it as a large footer background is a
  new role that should be recorded in the ADR index or a short
  color-usage note so we don't silently drift the token.

---

## Ticket 2 — Email-client button vs. inline contact form

### Research question
When a user clicks "Be our partner" / "Contact us", is launching the
system email client (`mailto:` or native share) still optimal and
acceptable at an enterprise/FAANG level, or is an inline form preferred?

### Scope
- Enterprise patterns (Google, Apple, Meta, Microsoft, Shopify, Stripe).
- Accessibility and older-adult usability (presbyopia, scam awareness,
  broken default mail clients).
- Geragogy: cognitive load, reversibility, and confidence preservation.
- Security: spam scraping, bot protection, data retention.
- Implementation effort in the current stack (Railway/FastAPI backend).

### Output
Research memo `.ai/research/2026-09-16-contact-form-vs-mailto.md`
with source table, decision matrix, and recommended pattern.

---

## Ticket 3 — Partner contact form

### Description
Create a contact/partner-inquiry form inspired by
`https://www.getsetup.com/about-us/contact-us` and wire the fat footer
"Be my partner" link to it.

### Acceptance criteria
- New route (e.g. `/partners` or `/contact/partners`) with a form.
- Fields to match GetSetUp's pattern where applicable:
  - Name, email, organization/facility, role, message.
  - Optional: phone, how did you hear about us, best time to reach.
- Backend-served copy where possible.
- A11y: labels, focus, error messages, confirmation.
- Submit path follows Ticket 2 recommendation (mailto fallback or
  backend endpoint).
- No email in the footer itself.

---

## Ticket 4 — Social media links

### Description
Add Instagram, TikTok, and YouTube presence to the fat footer.

### Acceptance criteria
- Footer contains the three platform names as external links.
- Each link uses a descriptive, senior-friendly label.
- URLs are backend-served or statically configured in a single place.
- Open in a new tab with `rel="noopener noreferrer"`.

### Geragogy / contract notes
- V1 contract prohibits icons without an ADR. Default implementation will
  be text-first platform labels. If icons are required, a discrete ADR is
  needed and each icon must be paired with an adjacent text label.

---

## Open questions

1. Exact Instagram, TikTok, and YouTube URLs for Mynaani.
2. Should the partner form submit to a new backend endpoint or use a
   mailto fallback while email infrastructure is decided?
3. Does the user want an ADR for icon usage, or text-only social links?
4. Should the footer "Be our partner" label be exactly "Be my partner"
   (as written in the ticket) or the existing "Be our partner"?
