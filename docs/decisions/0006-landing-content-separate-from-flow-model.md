# 0006 - Landing-page content is stored separately from the Golden Flow step model

## Status

Accepted (Sprint 5).

## Context

Sprint 3 locked the Golden Landing Flow as an 8-step **conceptual model** of user cognitive states (`LandingStep` in `backend/models/landing.py`): Arrival, What This Is, Is This For Me, Safety and Control, Low-Commitment Choice, First Guided Interaction, First Safe Win, Optional Continuation.

Sprint 5 introduces the **actual user-facing copy** for the landing page: hero, introduction, what-noni-does, how-it-feels, trust-and-safety, call-to-action, closing.

The two artifacts do not map 1:1, and attempting to force a 1:1 mapping would distort both:

- The 8-step flow includes post-interaction states (Steps 5-7) that have no correlate on a pre-click marketing surface. They require real Claude integration.
- The landing page is a traditional scrollable page with several sections, not a strict linear walk through 8 cognitive states.

## Decision

1. The 8-step `LandingStep` model (Sprint 3) remains the canonical **conceptual** specification of the first-visit user journey. It is served from `/api/landing/steps`.
2. The actual user-facing copy lives in `backend/content/landing_page.py` and is served from `/api/landing/page`. A Pydantic schema in `backend/models/landing_page.py` enforces the contract.
3. `LandingStep.display_title`, `display_body`, and `action_label` **remain `None`** in this sprint. The Sprint 3 contract test that asserts this continues to pass.
4. When a future sprint introduces a step-by-step interactive onboarding experience (Sprint 7, post real-Claude), that sprint may revisit this decision and populate `LandingStep.display_*` fields - or leave them permanently unused, noting the flow is a conceptual tool, not a rendering target.

## Consequences

- Frontend has two landing endpoints to reason about, with clearly different purposes.
- Copy changes ship without touching the flow model; flow-model changes ship without churning copy.
- Documentation now has a tidy pointer: "see ADR 0006" whenever someone wonders why both exist.
- Steps 5-7 of the Golden Flow have no finalized copy. This is expected and documented.
