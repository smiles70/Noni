# 0017 - Module 4 (building Claude Skills): same adaptation pattern as Modules 2-3

## Status

Accepted (Sprint 19).

## Context

A Module 4 drop-in was proposed: 6 units teaching learners to move from "using Claude" to "teaching Claude once" via Claude Skills - named, reusable, explicitly defined instruction packages that Claude invokes when relevant. Library-grounded: Carr (2009), Formosa (2012), Craik & Salthouse (2008), Lovden et al. (2010), Norman (2013), Fisk et al. (2009), Papert (1980); Claude Skills architecture (Anthropic, 2025-2026).

Module 4 is the first curriculum module that names a **real Anthropic product feature** (Claude Skills). Two consequences need explicit acknowledgement:

1. Rendering the Module 4 *content* requires no Anthropic API access. The content is declarative: it teaches *about* Skills using the same calm, page-based pattern as every other module.
2. Actually *creating* Skills end-to-end (the experience implied by units 3, 4, 5) requires Anthropic API integration and remains **vendor-blocked**.

The drop-in repeated the same architectural conflict that ADRs 0015 / 0016 already resolved: an endpoint that accepts a `signals` dict from the request body. That pattern remains forbidden under Rule 1 (Backend Authority).

## Decision

Module 4 lands following ADRs 0015 / 0016 verbatim:

- 6 units land **content-verbatim** (titles, descriptions, page text, thresholds, telemetry_requirements).
- `Module4Unit` in `backend/models/curriculum_units_module_4.py` mirrors `Module2Unit` / `Module3Unit`.
- Three endpoints under `/api/curriculum/module-4/`: `units`, `units/{id}`, `next`. None accept signals from the request body.
- `telemetry_requirements` recorded in `event_metadata` per ADR 0009.
- Per-learner enforcement remains deferred to the auth-vendor pass.
- The end-to-end Skill-creation experience (live wizard, Anthropic API calls, persistence, review/edit cycle) is **out of scope** until the Claude API vendor pass. The declarative content explains the concept and prepares learners; the interactive flow comes later.
- `Module2Unit` / `Module3Unit` / `Module4Unit` now carry identical fields. A shared `TelemetryGatedUnit` base is still deferred; the duplication is small and explicit. If a 5th module is proposed, the refactor lands first.

## Consequences

- Noni's curriculum is now 4 modules: orientation/safety -> sustained use -> long-term judgment -> building Skills. 15 units across Modules 1-3 plus 6 in Module 4 = **21 units**.
- Test coverage grows from 72 -> 79.
- The architectural rule that the frontend cannot supply ISCS signals stays intact across all four modules.
- `docs/deferred-decisions.md` is amended: a Claude Skills creation flow requires Anthropic API + auth (per-Skill ownership). Both are vendor-blocked.
- Future curriculum drop-ins should follow this pattern without further ADRs unless they introduce a new architectural concern.
