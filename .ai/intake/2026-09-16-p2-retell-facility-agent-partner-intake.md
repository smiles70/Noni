# Intake — Facility agent partner-inquiry tool + KB update via Retell API

**Date:** 2026-09-16
**Status:** in_progress
**Persona:** B2B — facility / partner journey only (per AGENTS.md
dual-audience rule)

## Problem statement

The facility chat agent (`agent_719be4f2578150bb27ac06f357`) mounted on
`/partners` doesn't know the partner-inquiry flow or its fields, and has
no way to submit one. Owner directive: Retell configuration is done via
the **Retell API from this codebase** — not the dashboard. The prior
`retell-mynaani/` config workspace is not in this repo (n8n-help-flow is
deprecated and excluded).

## Goal

1. In-repo Retell config artifacts so agent/KB state is versioned and
   reproducible:
   - KB document describing the `/partners` inquiry flow + fields.
   - `submit_partner_inquiry` custom-tool spec posting to
     `POST /api/v1/site/partner-inquiry`.
   - A push script (Python + httpx, already a dep) that applies both via
     the Retell API, gated on `RETELL_API_KEY`.
2. Persona isolation preserved: the tool + KB doc attach to the
   **facility** agent only — never the gift agent.

## Constraints / gaps

- `RETELL_API_KEY` is not in this repo — required to run the script.
- Chat-agent tool calling must degrade gracefully: if the tool fails,
  the agent falls back to quoting help@mynaani.com + the call line
  (existing escalation copy).
- No Retell config on the B2C learner journey; gift agent unchanged.

## Acceptance

- `retell/` (or equivalent) config dir in-repo with KB doc, tool spec,
  and idempotent push script.
- Script is dry-run safe and refuses to run without the key.
- Docs updated; memo addendum notes the real path.
