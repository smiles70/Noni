# Intake — Work Item Assignment from Chat: Prerequisites

**Date:** 2026-08-29  
**Process:** v9.51  
**Source skill:** `.devin/skills/work-item-assignment/SKILL.md`  
**Scope:** Define the human and runtime prerequisites required before the chat-to-GitHub work-item assignment capability can be used. No code is activated in this intake.

---

## Problem Statement

The `.devin/skills/work-item-assignment/SKILL.md` can turn a chat request into a GitHub issue and optionally add it to a project board, but the skill requires external conditions that are not currently confirmed: GitHub CLI authentication, Issues enabled, a known project board, a populated people map, and a permission check so work is never assigned to someone who cannot access the repository.

## Requirements

| ID | Requirement | Extraction method | Confidence |
|---|---|---|---|
| REQ-WI-001 | `gh` must be authenticated in the runtime environment before any command runs | structured_source | 0.95 |
| REQ-WI-002 | The `smiles70/Noni` repository must have GitHub Issues enabled | structured_source | 0.95 |
| REQ-WI-003 | A GitHub Projects v2 board must exist, and its project number must be known and recorded | structured_source | 0.95 |
| REQ-WI-004 | `.ai/people.yaml` must contain the common chat-name to GitHub-handle mappings used by the team | structured_source | 0.95 |
| REQ-WI-005 | Screenshots and other files referenced in chat must be attachable to the created issue body | structured_source | 0.90 |
| REQ-WI-006 | The assignee must have read access to `smiles70/Noni` before the issue can be assigned to them | structured_source | 0.95 |

## Capabilities to add

| ID | Capability | Notes |
|---|---|---|
| CAP-WI-AUTH | `gh auth status` pre-check | Fails fast if the token is missing or expired |
| CAP-WI-REPO | Repository access verifier | Uses `gh api repos/smiles70/Noni` to confirm Issues are enabled and the token has write access |
| CAP-WI-BOARD | Project board resolver | Uses `gh project list --owner smiles70` to find the board number and stores it in `.ai/people.yaml` or a config file |
| CAP-WI-PEOPLE | People mapper | Loads `.ai/people.yaml` and resolves chat names to GitHub handles |
| CAP-WI-ATTACH | File attachment builder | Converts screenshot paths or file references into issue body markdown or `gh issue create --body-file` with embedded base64/URL if required |
| CAP-WI-PERMISSION | Assignee permission check | Calls `gh api repos/smiles70/Noni/collaborators/{assignee}` or `gh api repos/smiles70/Noni/invitations` to confirm access |

## Non-goals

- Do **not** create any GitHub issue in this session.
- Do **not** run `gh auth login` or other interactive authentication commands.
- Do **not** add real GitHub handles to `.ai/people.yaml` unless the user provides them.
- Do **not** modify repository settings, branch protection, or member access.

## Open questions

1. Which GitHub account or token will the assistant use? Is it the user's personal token, a fine-grained PAT, or a GitHub App?
2. What is the correct project board number, and what columns should the issue land in?
3. Should screenshots be uploaded to the issue directly (GitHub supports image paste in the body) or stored elsewhere and linked?
4. Should the permission check block assignment or create the issue unassigned and ask the user to assign later?
5. Which users need to be in `.ai/people.yaml` for the first rollout?

## Artifacts to produce later

- `.ai/people.yaml` (populated)
- `.ai/config/work-item-config.yaml` (optional project number and default label)
- Updated `.devin/skills/work-item-assignment/SKILL.md` with the permission and attachment checks

## v9.51 traceability

- `Owner` for this intake: `OWN-PROCESS`
- `Persona` served: the process maintainer / product owner assigning work from chat
- `Journey` linked: `JRN-FREE-TO-PAID` (incidental) — the assignment skill may be used to hand off any work stream, including payment defects
- `Gap` opened: `GAP-WI-001` — skill cannot be used until all prerequisites are confirmed
