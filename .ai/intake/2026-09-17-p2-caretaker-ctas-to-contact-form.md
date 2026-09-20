# Intake — caregiver page CTAs route to /contact, not mailto

- Priority: P2 (UX correctness — owner-reported; ontology sweep of the
  same defect class as the facility ticket)
- Date: 2026-09-17
- Persona: **caregiver / gift-giver** — /caregiver only.

## Discovery (ontology sweep)

The defect class "button opens an email-provider picker" appears on
/caregiver in the same three shapes as /for-communities:

| Element | Was | Becomes |
| --- | --- | --- |
| Research-updates card secondary CTA | `mailto:` "Email us to join the list" | `Link` → `/contact`, "Request research updates" |
| Gift section secondary CTA | `mailto:` "Ask a question first" | `Link` → `/contact`, same label |
| "Questions before you give" primary CTA | `mailto:` "Email hello@mynaani.com" | `Link` → `/contact`, "Let's talk" |

Routing choice: `/contact` (shared form), **not** `/partners` — the
caregiver persona must never land on the facility form (AGENTS.md
dual-audience rule). Unused `CONTACT`/`MAILTO`/`UPDATES_MAILTO`
constants removed.

## Out of scope

Same as the facility intake: prose `help@mynaani.com` links and form
mailto fallbacks stay.
