# Intake — Paywall boundary UI copy drift

**Date:** 2026-09-12  
**Process:** v9.51  
**Status:** Resolved — implementation complete, awaiting staging verification  
**Source:** Live-site scan + user review of n8n help flow content  

---

## Problem

The approved intake `2026-09-06-paywall-boundary-m2-001` moved the free/paid module boundary:

- **Free:** Modules 0 and 1
- **Paid:** Modules 2, 3, 4, and 5

The curriculum enforcement code was updated: `backend/api/routes/curriculum.py` applies `paid_bundle_dep` to Module 2+ routes.

However, the user-facing copy was **not** updated. The live site and the in-repo UI still say:

> "Modules 0, 1, and 2 are free. ... Modules 3, 4, and 5 require a one-time purchase."

This is now false. Users who read the help page or the paywall page will receive the old rule. The widget, if it answers from the live help content, will also give the wrong answer.

---

## Affected surfaces

- `frontend/src/components/HelpPage.tsx` — "Free and paid modules" section
- `frontend/src/components/PaywallPage.tsx` — paywall copy (still says "Modules 3, 4, and 5")
- `frontend/src/components/CurriculumMenu.tsx` and `/menu` — menu docstring says "Modules 3+"
- `docs/content/help-caregiver-persona.md` — caregiver FAQ still references old boundary
- `docs/content/help-facility-persona.md` — facility FAQ still references old boundary
- `docs/requirements/PROBLEM-STATEMENT-N8N-HELP-002.md` — cites module split
- Live `/help` at `https://www.mynaani.com/help`

---

## Consequences

1. **Learner confusion:** A learner may finish Module 1, expect to continue into Module 2, and immediately hit a paywall they were not told about.
2. **Incorrect widget answers:** The n8n help widget, if it uses the help page or the draft caregiver/facility FAQs, will answer "Modules 0, 1, and 2 are free."
3. **Loss of trust:** The public help and the actual product behavior contradict each other.
4. **Caregiver/facility risk:** A caregiver buying a gift may believe the recipient will get more free content than is actually offered.

---

## What needs to happen

1. Update all user-facing copy to the new boundary:
   - Free = Modules 0 and 1
   - Paid = Modules 2, 3, 4, and 5
2. Ensure the paywall page, help page, curriculum menu, and gift/paywall flow all say the same thing.
3. Update the caregiver and facility help files used by the n8n flow.
4. Re-stage and re-scan to confirm live text is consistent.

---

## Open questions

- What is the current exact price for the paid bundle (Module 2–5)?
- Does the gift edition also grant access to Modules 2–5?
- Is the menu copy in `CurriculumMenu.tsx` also out of date?
- Should the widget explicitly mention that Module 2 is now the first paid module?
