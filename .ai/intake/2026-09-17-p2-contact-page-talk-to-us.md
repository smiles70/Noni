# Intake — /contact page + Talk-to-us routing + footer contact-line removal

- Priority: P2 (UX correctness — user-reported)
- Date: 2026-09-17
- Persona: **shared surface** — /contact serves both B2C and B2B
  audiences; no persona-specific pricing, no ChatWidget.

## Request (owner, verbatim)

"we did not want a text line for the connect with us item you just did
so remove that from all footers where it appears, we have a 'talk to
us' button and right now when you click it it launches an email app
selector which it should not so replace launching the email selection
box with a page that says 'we'd love to hear from you' and then lists
the phone and then a form that matches or style shape lay etc that
captures first name, last name and email and phone number"

## Scope

1. Remove the `contact_line` ("We'd love to connect with you…") block
   from the fat footer — backend content key, model field, Footer.tsx
   render + fallback, client interface, tests.
   Keep `contact_phone`/`contact_email` in the payload: the /partners
   hero and the new /contact page consume them.
2. Repoint the "Talk to us" header CTA on /for-communities from
   `mailto:` to `/contact`. TermsPage's inline "Talk to us first"
   sentence stays a mailto — it is inline copy, not the button.
3. New `/contact` page: H1 "We'd love to hear from you", the toll-free
   phone line, and a form capturing first name, last name, email,
   phone — styled on the PartnershipInquiryPage pattern (16px+ fields,
   labels above inputs, 44px targets, honeypot, calm thank-you state).
4. Backend `POST /api/v1/site/contact-inquiry` — ContactInquiry model
   (first_name, last_name, email, phone, honeypot website), emailed to
   CONTACT_EMAIL (help@mynaani.com) via the existing email service off
   the request path. Frontend falls back to mailto if unreachable —
   same no-lost-message contract as /partners.

## Edge cases

- Honeypot filled → synthetic receipt, no email (same as partners).
- Endpoint down → mailto fallback preserves the message.
- Footer payload without contact_line → Footer simply omits the block;
  `contact_phone`/`contact_email` still served for other consumers.
- Empty phone on /contact → phone paragraph hidden (empty-string
  contract), form still works.
