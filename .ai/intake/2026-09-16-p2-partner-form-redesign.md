# Intake — /partners form redesign (GetSetUp mimicry)

**Date:** 2026-09-16
**Status:** in_progress
**Problem:** The shipped `PartnershipInquiryPage` is a bare stacked form —
visually plain, not in our brand language, no radio buttons, does not mimic
the GetSetUp contact/demo model. Owner feedback: "ugly, doesn't match our
colors, isn't appealing, no radio buttons, does not mimic the model site
at all."

## Goal

Rebuild the page to match the GetSetUp contact surface:

- Branded hero area using the sage/desaturated green + surface tokens
  (same family as the fat footer).
- Calm headline + one-line purpose copy ("If you are an organization
  serving adults 55+ ...").
- Card-based form on `COLORS.surface` with `RADIUS.lg`, `SPACING` rhythm.
- Radio-button group for "What best describes your organization?"
  (Senior living community / Health plan or insurer / Caregiver network /
  Other) — radios are better than dropdowns for 4 or fewer options and
  show all choices at once (older-adult friendly). Requires a geragogy
  contract exception — see ADR.
- Fields: first name, last name, work email, organization name,
  phone (optional), message.
- Clear privacy line under the submit button ("We only use this to reply
  about partnership — no marketing list.").
- Thank-you state preserved.

## Acceptance

- Visual match to GetSetUp pattern within our token system.
- Radio group fully keyboard/screen-reader accessible (fieldset+legend).
- axe clean on `/partners`; unit + e2e coverage.
