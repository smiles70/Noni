# Intake — facility page CTAs route to the senior-care form, not mailto

- Priority: P2 (UX correctness — owner-reported)
- Date: 2026-09-17
- Persona: **facility / B2B** — /for-communities only.

## Request (owner, verbatim)

"the 'Start a conversation … Email hello@mynaani.com' button should say
'let's talk' or 'reach out' and it should link to the senior care form"

## Scope

1. "Start a conversation" primary CTA on /for-communities: label
   becomes **Let's talk**, `mailto:` → `<Link to="/partners">` (the
   senior-care facility inquiry form).
2. "Get research updates" card secondary CTA "Email us to join the
   list" → button labeled **Request research updates** (honest: it
   opens a form, not a blog), routed to `/partners`.
3. Procurement block inline `hello@mynaani.com` mailto → `<Link>` to
   `/partners` labeled "send us a note" (link text must match
   destination — WCAG 2.4.4).
4. After repoints, `CONTACT`/`MAILTO`/`UPDATES_MAILTO` constants are
   unused on this page and removed.

## Out of scope

Inline `help@mynaani.com` links inside prose on /help, /privacy,
/terms, and SupportContact — they display the real address in
sentence context and are not button CTAs. Form mailto *fallbacks* on
/partners and /contact remain (no-lost-message contract).
