# Intake — Footer "Contact us" line on all footers

**Date:** 2026-09-16
**Status:** implemented — verifying

## Problem

Every footer should carry a simple contact invitation: a calm sentence
("We'd love to connect with you."), the toll-free phone number, and the
public email address.

## Implementation

- `site_chrome.py`: `contact_line` copy. A `Contact` entry in
  `mini_links` was tried and **reverted**: two consecutive UAT failures
  on `ec38dd3` (6 mobile-iphone CTA timeouts, up from 1) correlate with
  the wider strip crowding the hero CTA — matches the flake mechanism in
  `2026-09-16-p1-mobile-iphone-cta-timeout.md`. Mini strip stays
  minimal per its own contract.
- `models/site_chrome.py`: `contact_email` + `contact_line` fields.
- `config.py`: `CONTACT_EMAIL` (default `help@mynaani.com`, matching
  the address already published on /help); phone reuses `PARTNER_PHONE`
  (`+1 (877) 409-4144`, the Retell-answered toll-free line).
- `site.py` `/footer`: injects both contact values from settings.
- `Footer.tsx`: contact row above the hairline — invitation sentence +
  `tel:` link (E.164) + `mailto:` link; renders only when a detail is
  present; static fallback carries the real values so contact info
  survives an API outage.
- `LandingFooter.tsx`: fallback `mini_links` gains `Contact → /help`;
  link keys switched to `label` (Help and Contact share `/help`).

## Edge cases

- Empty `contact_phone`/`contact_email` → row hidden entirely.
- Both links keep ≥ touch-target and surface-tone contrast on the
  sage footer background (same tokens as existing links).
