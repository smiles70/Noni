# 0015 - Module 2 multi-dimensional ISCS gating: data shape kept, request-body signals rejected

## Status

Accepted (Sprint 17).

## Context

A drop-in proposal for a "Module 2" curriculum (sustained, real-world Claude use over time) was provided. The intent is sound and library-grounded: Carr (2009), Formosa (2012), Lövdén et al. (2010), Park et al. (2014), Norman (2013), Fisk et al. (2009), Wiener (1948). Each unit declared a `telemetry_requirements` dict with keys like `volatility_max`, `strain_max`, `mastery_min` - per-learner geragogy signals that should gate progression.

The proposal also wired an endpoint that accepted a `signals` dict from the **request body** and passed it to a governor `approve(candidates, signals)`. That pattern is **explicitly disallowed** by ARCHITECTURE.md Rule 1 (Backend Authority) and the architectural pattern established in Sprint 2 / ADR 0007: ISCS-gated endpoints derive stability from the server-side [InterfaceStateEstimator](cci:2://file:///mnt/c/Users/kimem/Noni/backend/core/interface_control/state_estimator.py:10:0-25:42) and never trust client-supplied signals.

## Decision

**Accept the data, reject the wiring.**

- The 5 Module 2 units land verbatim in content (titles, descriptions, page text, thresholds, telemetry_requirements).
- A new `Module2Unit` model in `backend/models/curriculum_units_module_2.py` extends the existing `CurriculumUnit` with a typed `telemetry_requirements: Dict[str, float]` field. The base model is untouched; Module 1 is unaffected.
- Endpoints follow the Sprint 10 pattern: `/api/curriculum/module-2/units`, `/api/curriculum/module-2/units/{id}`, `/api/curriculum/module-2/next`. None accept signals from the request body. Stability is derived from the running [InterfaceStateEstimator](cci:2://file:///mnt/c/Users/kimem/Noni/backend/core/interface_control/state_estimator.py:10:0-25:42).
- `telemetry_requirements` are recorded in audit telemetry at every decision point (per ADR 0009) inside `event_metadata`. The audit columns themselves are unchanged.
- Enforcement of `volatility_max` / `strain_max` / `mastery_min` is **deferred** because Noni does not yet track per-learner state. Once auth lands (vendor pass), those gates can be applied without further model changes.

## Consequences

- The library-grounded geragogy intent is preserved as data, queryable today, enforceable once auth lands. No information is lost.
- The architectural rule that the frontend cannot supply ISCS signals stays intact across both modules.
- A future ADR (post-auth) will document how the gates are applied and which estimator owns each per-learner signal.
- Test coverage now includes content invariants (no urgency language, all units have `telemetry_requirements` with values in `[0, 1]`) and audit-log verification (every Module 2 decision produces an `iscs_decision` row carrying `telemetry_requirements` in `event_metadata`).
