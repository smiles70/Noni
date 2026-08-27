# Mynaani Knowledge Graph and Traceability Report

**Process:** v9.51 ontology and traceability protocol
**Date:** 2026-08-27
**Repo:** smiles70/Mynaani
**Nodes:** 140 | **Edges:** 159

## Ontology

Entities: `SourceArtifact`, `Requirement`, `Capability`, `Epic`, `UserStory`, `AcceptanceCriterion`, `Test`, `Evidence`, `Owner`, `Decision`, `Dependency`, `Gap`, `Conflict`, `Assumption`.

Relationships: `defines`, `mandates`, `enforces`, `supports`, `implemented_by`, `verified_by`, `evidenced_by`, `shapes`, `authorizes`, `informs`, `consolidates`, `depends_on`, `blocked_by`, `has_gap`, `owns`.

## Traceability Summary

| From | Relationship | To | Provenance |
|---|---|---|---|
| SRC-README | defines | REQ-001 | README.md §1 |
| SRC-README | defines | REQ-002 | README.md §3 |
| SRC-README | defines | REQ-003 | README.md §3 |
| SRC-README | defines | REQ-004 | README.md §3 |
| SRC-ARCH | mandates | REQ-005 | ARCHITECTURE.md Rule 5 |
| SRC-ARCH | mandates | REQ-006 | ARCHITECTURE.md Rule 6 |
| SRC-ARCH | mandates | REQ-007 | ARCHITECTURE.md Rule 7 |
| SRC-ARCH | mandates | REQ-008 | ARCHITECTURE.md Rule 9 |
| SRC-ARCH | mandates | REQ-009 | ARCHITECTURE.md Rule 10 |
| SRC-ARCH | mandates | REQ-001 | ARCHITECTURE.md Rule 8 |
| SRC-CONTRACT | mandates | REQ-010 | CONTRACT.md §IV.A |
| SRC-CONTRACT | mandates | REQ-011 | CONTRACT.md §IV.B |
| SRC-CONTRACT | mandates | REQ-012 | CONTRACT.md §I |
| SRC-ADR-0019 | enforces | REQ-010 | ADR 0019 §4 |
| SRC-ADR-0019 | enforces | REQ-011 | ADR 0019 §4 |
| SRC-ADR-0019 | enforces | REQ-012 | ADR 0019 §2 |
| SRC-ADR-0021 | enforces | REQ-013 | ADR 0021 §(1) |
| SRC-ADR-0021 | enforces | REQ-014 | ADR 0021 §(4) |
| SRC-ADR-0021 | enforces | REQ-015 | ADR 0021 §(5) |
| SRC-LIB-README | supports | REQ-012 | docs/library/README.md |
| REQ-001 | implemented_by | CAP-001 | ISCS protects cognitive safety |
| REQ-002 | implemented_by | CAP-002 | UI state governed by backend |
| REQ-003 | implemented_by | CAP-003 | RenderGuard enforces passivity |
| REQ-004 | implemented_by | CAP-004 | Curriculum API preserves history |
| REQ-005 | implemented_by | CAP-005 | Landing API has no urgency |
| REQ-006 | implemented_by | CAP-006 | Billing follows non-dark-pattern model |
| REQ-007 | implemented_by | CAP-008 | Telemetry export enables review |
| REQ-008 | implemented_by | CAP-009 | Telemetry summary supports audit |
| REQ-010 | implemented_by | CAP-002 | UI envelope returned |
| REQ-011 | implemented_by | CAP-003 | RenderGuard validates |
| REQ-012 | implemented_by | CAP-003 | Closed component inventory |
| REQ-013 | implemented_by | CAP-004 | Free modules 1-3 |
| REQ-014 | implemented_by | CAP-006 | One-time purchase, no subscriptions |
| REQ-015 | implemented_by | CAP-004 | Paywall at module boundary |
| REQ-016 | implemented_by | CAP-013 | axe-playwright E2E |
| REQ-017 | implemented_by | CAP-012 | verify-bundle.mjs |
| REQ-018 | implemented_by | CAP-012 | npm audit |
| CAP-012 | verified_by | TEST-002 | build command |
| CAP-012 | verified_by | TEST-007 | bundle verification script |
| CAP-013 | verified_by | TEST-001 | type-check |
| CAP-013 | verified_by | TEST-003 | unit tests |
| CAP-014 | verified_by | TEST-005 | test_iscs.py |
| CAP-014 | verified_by | TEST-006 | test_geragogy_signals.py |
| CAP-014 | verified_by | TEST-008 | full suite (blocked) |
| CAP-006 | verified_by | TEST-004 | npm audit |
| CAP-001 | verified_by | TEST-005 | test_iscs.py |
| CAP-002 | verified_by | TEST-008 | full envelope tests |
| CAP-012 | evidenced_by | EVI-001 | dist/ generated |
| CAP-013 | evidenced_by | EVI-002 | test output |
| CAP-006 | evidenced_by | EVI-003 | package-lock.json |
| CAP-001 | evidenced_by | EVI-004 | test_iscs.py |
| CAP-017 | evidenced_by | EVI-005 | PRA report |
| CAP-016 | evidenced_by | EVI-006 | Nelson scorecard |
| DEC-001 | shapes | CAP-005 | Landing API |
| DEC-002 | shapes | CAP-002 | UI envelope |
| DEC-002 | shapes | CAP-003 | RenderGuard |
| DEC-003 | shapes | CAP-006 | Billing model |
| SRC-ADR-0019 | authorizes | DEC-002 | closed contract |
| SRC-ADR-0021 | authorizes | DEC-003 | pricing |
| SRC-IDD | informs | SRC-CONTRACT | IDD Section II informs UI contract |
| SRC-IDD | informs | SRC-PROJECT-INTENT | IDD is core provenance |
| SRC-PROJECT-INTENT | consolidates | SRC-README | Synthesis |
| SRC-PROJECT-INTENT | consolidates | SRC-IDD | Synthesis |
| SRC-PROJECT-INTENT | consolidates | SRC-COMPETITOR | Synthesis |
| CAP-007 | depends_on | DEP-001 | Auth API needs auth vendor |
| CAP-004 | depends_on | DEP-003 | numpy for ISCS |
| CAP-014 | depends_on | DEP-004 | Postgres for full tests |
| CAP-004 | depends_on | DEP-002 | Real Claude for Module 4/5 |
| REQ-002 | blocked_by | GAP-001 | Full test evidence missing |
| CAP-014 | blocked_by | GAP-001 | Cannot run full backend suite |
| CAP-001 | has_gap | GAP-004 | No CHARTER.md |
| SRC-README | has_gap | GAP-004 | Charter distributed |
| SRC-README | has_gap | GAP-005 | Personas distributed |
| OWN-001 | owns | CAP-012 | Engineering |
| OWN-001 | owns | CAP-014 | Engineering |
| OWN-002 | owns | DEC-003 | Product |
| OWN-002 | owns | REQ-005 | Product |
| SRC-MAGIC-INTAKE | defines | FR-001 | intake FR section |
| SRC-MAGIC-INTAKE | defines | NFR-001 | intake NFR section |
| SRC-MAGIC-ADR | authorizes | DEC-0027 | ADR 0027 |
| DEC-0027 | shapes | FR-001 | provider selection |
| DEC-0027 | shapes | TR-001 | provider selection |
| DEC-0027 | shapes | CAP-MAGIC-SDK | provider selection |
| DEC-0027 | shapes | CAP-MAGIC-ADMIN | provider selection |
| FR-001 | implemented_by | CAP-MAGIC-CONFIG | AUTH_PROVIDER=magic |
| FR-002 | implemented_by | CAP-MAGIC-LOGIN | loginWithMagicLink |
| FR-003 | implemented_by | CAP-MAGIC-VERIFIER | validate_did_token |
| FR-004 | implemented_by | CAP-MAGIC-ADMIN | account materialization |
| TR-001 | implemented_by | CAP-MAGIC-ADMIN | magic-admin dependency |
| TR-002 | implemented_by | CAP-MAGIC-SDK | magic-sdk dependency |
| TR-003 | implemented_by | CAP-MAGIC-ADMIN | MagicAuthProvider |
| TR-004 | implemented_by | CAP-MAGIC-VERIFIER | magic_verifier.py |
| CAP-MAGIC-VERIFIER | verified_by | TEST-MAGIC-VERIFIER | pytest |
| CAP-MAGIC-LOGIN | verified_by | TEST-MAGIC-AUTH-FE | vitest |
| CAP-MAGIC-ADMIN | evidenced_by | EVI-MAGIC-ADR | ADR 0027 |
| CAP-MAGIC-SDK | evidenced_by | EVI-MAGIC-PLAN | integration plan |
| CAP-MAGIC-VERIFIER | depends_on | DEP-MAGIC-ADMIN | package install |
| CAP-MAGIC-SDK | depends_on | DEP-MAGIC-SDK-FE | package install |
| CAP-MAGIC-LOGIN | depends_on | DEP-MAGIC-ACCOUNT | dashboard key |
| FR-002 | blocked_by | GAP-MAGIC-IMPL | not implemented yet |
| FR-003 | has_gap | GAP-MAGIC-SESSION-REFRESH | DID short lifetime |
| OWN-MAGIC | owns | CAP-MAGIC-ADMIN | engineering |
| OWN-MAGIC | owns | CAP-MAGIC-SDK | engineering |
| SRC-FRD-AUTH-001 | defines | FR-001 | FRD-AUTH-001 FR-001 |
| SRC-FRD-AUTH-001 | defines | FR-002 | FRD-AUTH-001 FR-002 |
| SRC-FRD-AUTH-001 | defines | FR-003 | FRD-AUTH-001 FR-003 |
| SRC-FRD-AUTH-001 | defines | FR-004 | FRD-AUTH-001 FR-004 |
| SRC-FRD-AUTH-001 | defines | FR-005 | FRD-AUTH-001 FR-005 |
| SRC-FRD-AUTH-001 | defines | FR-006 | FRD-AUTH-001 FR-006 |
| SRC-FRD-AUTH-001 | defines | FR-007 | FRD-AUTH-001 FR-007 |
| SRC-FRD-AUTH-001 | defines | FR-008 | FRD-AUTH-001 FR-008 |
| SRC-PRD-AUTH-001 | defines | NFR-001 | PRD-AUTH-001 NFR-001 |
| SRC-PRD-AUTH-001 | defines | NFR-002 | PRD-AUTH-001 NFR-002 |
| SRC-PRD-AUTH-001 | defines | NFR-003 | PRD-AUTH-001 NFR-003 |
| SRC-PRD-AUTH-001 | defines | NFR-004 | PRD-AUTH-001 NFR-004 |
| SRC-PRD-AUTH-001 | defines | NFR-005 | PRD-AUTH-001 NFR-005 |
| SRC-PRD-AUTH-001 | defines | NFR-006 | PRD-AUTH-001 NFR-006 |
| SRC-PRD-AUTH-001 | defines | TR-001 | PRD-AUTH-001 TR-001 |
| SRC-PRD-AUTH-001 | defines | TR-002 | PRD-AUTH-001 TR-002 |
| SRC-PRD-AUTH-001 | defines | TR-003 | PRD-AUTH-001 TR-003 |
| SRC-PRD-AUTH-001 | defines | TR-004 | PRD-AUTH-001 TR-004 |
| SRC-PRD-AUTH-001 | defines | TR-005 | PRD-AUTH-001 TR-005 |
| SRC-PRD-AUTH-001 | defines | TR-006 | PRD-AUTH-001 TR-006 |
| SRC-PRD-AUTH-001 | defines | TR-007 | PRD-AUTH-001 TR-007 |
| SRC-PRD-AUTH-001 | defines | TR-008 | PRD-AUTH-001 TR-008 |
| SRC-PRD-AUTH-001 | defines | TR-009 | PRD-AUTH-001 TR-009 |
| SRC-PRD-AUTH-001 | defines | TR-010 | PRD-AUTH-001 TR-010 |
| SRC-BRD-AUTH-001 | defines | BRG-001 | BRD-AUTH-001 B-001 |
| SRC-BRD-AUTH-001 | defines | BRG-002 | BRD-AUTH-001 B-002 |
| SRC-BRD-AUTH-001 | defines | BRG-003 | BRD-AUTH-001 B-003 |
| SRC-BRD-AUTH-001 | defines | BRG-004 | BRD-AUTH-001 B-004 |
| SRC-MAGIC-ADR | informs | SRC-BRD-AUTH-001 | ADR 0027 drives business goals |
| SRC-MAGIC-INTAKE | informs | SRC-FRD-AUTH-001 | intake FRs |
| SRC-MAGIC-INTAKE | informs | SRC-PRD-AUTH-001 | intake NFRs/TRs |
| BRG-001 | implemented_by | FR-002 | passwordless flow reduces abandonment |
| BRG-002 | implemented_by | FR-002 | magic links eliminate passwords |
| BRG-003 | implemented_by | NFR-002 | vendor dark-pattern guard |
| BRG-004 | implemented_by | FR-001 | real provider selection |
| SRC-MAGIC-RESEARCH | informs | CAP-MAGIC-VERIFIER | DID validation edge cases |
| SRC-MAGIC-RESEARCH | informs | CAP-MAGIC-LOGIN | sign-in UX and redirect |
| SRC-MAGIC-RESEARCH | informs | CAP-MAGIC-SDK | session/token lifetime |
| SRC-MAGIC-RESEARCH | informs | FR-003 | DID validation edge cases |
| SRC-MAGIC-RESEARCH | informs | FR-004 | subject ID edge case E-007 |
| CAP-MAGIC-VERIFIER | has_gap | GAP-MAGIC-SUBJECT-ID | must hash sub |
| CAP-MAGIC-LOGIN | has_gap | GAP-MAGIC-REDIRECT | redirectURI decision |
| CAP-MAGIC-SDK | has_gap | GAP-MAGIC-REFRESH | 15-min DID lifetime |
| CAP-MAGIC-VERIFIER | has_gap | GAP-MAGIC-TEST-MODE | mock test data |
| CAP-MAGIC-SDK | depends_on | ASM-MAGIC-EMAIL | deliverability |
| CAP-MAGIC-SDK | depends_on | ASM-MAGIC-FREE-TIER | pricing |
| CAP-MAGIC-LOGIN | depends_on | ASM-MAGIC-AUTH-APP | correct app type |
| CAP-MAGIC-VERIFIER | evidenced_by | EVI-MAGIC-VERIFY-TEST | pytest test_magic_verifier.py |
| CAP-MAGIC-SDK | evidenced_by | EVI-MAGIC-TC | npm run type-check |
| CAP-MAGIC-SDK | evidenced_by | EVI-MAGIC-UNIT | npm run test:unit |
| CAP-MAGIC-SDK | evidenced_by | EVI-MAGIC-BUILD | npm run build |
| CAP-MAGIC-LOGIN | evidenced_by | EVI-MAGIC-UNIT | SignInPage tests |
| TEST-MAGIC-VERIFIER | evidenced_by | EVI-MAGIC-VERIFY-TEST | test run |
| SRC-FRD-AUTH-001 | implemented_by | CAP-MAGIC-LOGIN | Phase 1-3 implementation |
| SRC-PRD-AUTH-001 | implemented_by | CAP-MAGIC-VERIFIER | Phase 1-3 implementation |
| SRC-BRD-AUTH-001 | implemented_by | CAP-MAGIC-SDK | Phase 1-3 implementation |

## Magic.link implementation status

Capabilities `CAP-MAGIC-*` are now implemented. Evidence nodes link to test and build results. `GAP-MAGIC-IMPL` is closed.

## Key Traceability Chains

1. **BRD-AUTH-001 -> BRG-* -> FR-* -> CAP-MAGIC-***
2. **FRD-AUTH-001 / PRD-AUTH-001 -> CAP-MAGIC-* -> Test / Evidence**
3. **ADR 0027 -> CAP-MAGIC-* -> Evidence**

## Identified Gaps

| ID | Gap | Reason |
|---|---|---|
| GAP-001 | No live Postgres/Redis | Docker unavailable in sandbox; full backend suite blocked |
| GAP-002 | No SIEM integration | Not configured; logs stdout only |
| GAP-003 | No Lighthouse/pa11y baseline | Not established |
| GAP-004 | No canonical CHARTER.md | Purpose distributed across README, ARCHITECTURE, IDD, ADRs |
| GAP-005 | No PERSONAS.md | Audience inferred from IDD and ADRs |
| GAP-MAGIC-SESSION-REFRESH | DID 15-minute token refresh strategy not defined | Needs ADR/clarification for long learning sessions |
| GAP-MAGIC-SUBJECT-ID | Magic auth_user_id should derive from sub, not email | Research edge case E-007 |
| GAP-MAGIC-REDIRECT | Decision needed on redirectURI and callback page | Research edge case E-006 |
| GAP-MAGIC-REFRESH | DID token 15-min refresh strategy not defined | Research issue 3.1 |
| GAP-MAGIC-TEST-MODE | Need dedicated test-mode tenant and CI config | Research issue 3.6 |

## Artifacts

- Machine-readable graph: `.ai/process/KNOWLEDGE_GRAPH.json`
- This report: `.ai/process/KNOWLEDGE_GRAPH.md`
- Phase inventory: `.ai/process/PHASE_INVENTORY.md`
- Implementation research: `.ai/process/MAGIC_IMPLEMENTATION_RESEARCH.md`
- Business requirements: `docs/requirements/BRD.md`
- Functional requirements: `docs/requirements/FRD.md`
- Product requirements: `docs/requirements/PRD.md`

*Generated under Process v9.51.*

## Railway migration

- `DEC-RAILWAY-001` authorizes `EPIC-RAILWAY-MIGRATION`.
- Capabilities `CAP-RAILWAY-*` are pending.
- `GAP-RAILWAY-TOKEN` tracks the missing `RAILWAY_TOKEN`.
- `EVI-RAILWAY-PLAN` is the migration plan.


## Railway migration verification (2026-08-27)

- `CAP-RAILWAY-DEPLOY`, `CAP-RAILWAY-SECRETS`, `CAP-RAILWAY-ENV`, `CAP-RAILWAY-SMOKE` marked `implemented`.
- `GAP-RAILWAY-TOKEN` remains open until `RAILWAY_TOKEN` is configured.
- `EVI-RAILWAY-CODE` records the code changes.

## Landing hero redesign (HERO-001) — 2026-08-27

- `SRC-HERO-INTAKE` defines `REQ-HERO-001` through `REQ-HERO-006`.
- `BRD-HERO-001` defines `BRG-HERO-001` (business goal).
- `FRD-HERO-001` defines `FR-HERO-001` through `FR-HERO-005`.
- `PRD-HERO-001` defines `NFR-HERO-001` through `NFR-HERO-005` and `TR-HERO-001` through `TR-HERO-003`.
- `SRC-ADR-0028` authorizes `DEC-0028`.
- `DEC-0028` shapes `CAP-HERO-LANDING`.
- `CAP-HERO-LANDING` depends_on `DEP-HERO-IMAGE` (hero image asset).
- `CAP-HERO-LANDING` verified_by `TEST-HERO-TYPECHECK`, `TEST-HERO-BUILD`, `TEST-HERO-BUNDLE`.
- `GAP-HERO-IMAGE` remains open until a Mynaani-appropriate hero image is sourced.
- `EVI-HERO-RESEARCH` is `.ai/process/LANDING_HERO_REDESIGN_RESEARCH.md`.
- `PHASE-HERO-0` pre-flight is `PREFLIGHT_HERO.md` and status is `GO`.
- `CAP-HERO-LANDING` is `implemented_by` `frontend/src/components/LandingPage.tsx`.
- `EVI-HERO-BUILD` is `npm run type-check` and `npm run build` passing.
- `EVI-HERO-DEPLOY` is Cloudflare Pages deploy of `noni-web.pages.dev/assets/index-NwLzaeT9.js`.
- `DEC-0028` status updated to `Accepted`.

## HERO-001 landing page competitive analysis (2026-08-27)

- `SRC-HERO-COMP-RESEARCH` is `.ai/process/LANDING_HERO_COMPETITIVE_RESEARCH.md`.
- `SRC-HERO-RUBRIC` is `.ai/process/LANDING_HERO_RUBRIC.md`.
- `SRC-HERO-GAP` is `.ai/process/LANDING_HERO_GAP_ANALYSIS.md`.
- `SRC-ADR-0029` is `docs/decisions/0029-landing-hero-contract-exemption.md`.
- `SRC-HERO-GAP` identifies `GAP-HERO-HEADLINE` (headline below competitor size).
- `SRC-HERO-GAP` identifies `GAP-HERO-BENEFITS` (no benefit cards above fold).
- `SRC-HERO-GAP` identifies `GAP-HERO-TRUST` (missing explicit trust signal).
- `DEC-0029` proposes partial contract exemption for `LandingPage.tsx`.

## HERO-002 contract-exempt landing hero redesign (2026-08-27)

- `SRC-HERO-002-INTAKE` is `.ai/intake/2026-08-27-landing-hero-exemption-redesign.md`.
- `DEC-0029` status updated to `Accepted`.
- `SRC-PHASE-HERO-EXEMPT` is `.ai/process/PHASE_INVENTORY_HERO_EXEMPT.md`.
- `SRC-PREFLIGHT-HERO-EXEMPT` is `.ai/process/PREFLIGHT_HERO_EXEMPT.md`.
- `SRC-LESSONS-HERO` is `.ai/process/LESSONS_LEARNED_HERO.md`.
- `GAP-HERO-HEADLINE` resolution path: increase `LandingPage.tsx` H1 via `ADR 0029`.
- `GAP-HERO-TRUST` resolution path: add "Free. No card needed." note to primary CTA.
- `CAP-HERO-LANDING-EXEMPT` depends_on `DEP-HERO-IMAGE` (placeholder `nonisplash.jpg`).
- `EVI-HERO-002-PREFLIGHT` is `PREFLIGHT_HERO_EXEMPT.md` with `GO` status.
- `EVI-HERO-002-DEPLOY` is live bundle `https://noni-web.pages.dev/assets/index-BQ6GAP4z.js`.
- `CAP-HERO-LANDING-EXEMPT` status is `implemented`.

## HERO-003 full-page hero image update (2026-08-27)

- `SRC-HERO-003-INTAKE` is `.ai/intake/2026-08-27-landing-hero-image-update.md`.
- `SRC-PHASE-HERO-IMAGE` is `.ai/process/PHASE_INVENTORY_HERO_IMAGE.md`.
- `SRC-PREFLIGHT-HERO-IMAGE` is `.ai/process/PREFLIGHT_HERO_IMAGE.md`.
- `SRC-LESSONS-HERO-IMAGE` is `.ai/process/LESSONS_LEARNED_HERO_IMAGE.md`.
- `GAP-HERO-IMAGE-LEFT` resolution path: use `object-position: left center`.
- `CAP-HERO-LANDING-EXEMPT` `refines` to `CAP-HERO-LANDING-FULLPAGE`.
- `EVI-HERO-003-PREFLIGHT` is `PREFLIGHT_HERO_IMAGE.md` with `GO` status.
- `EVI-HERO-003-DEPLOY` is live bundle `https://noni-web.pages.dev/assets/index-BDTGBJ7j.js`.
- `CAP-HERO-LANDING-FULLPAGE` status is `implemented`.

## HERO-004 mynaani hero image swap (2026-08-27)

- `SRC-HERO-004-INTAKE` is `.ai/intake/2026-08-27-landing-hero-mynaani-image.md`.
- `SRC-PHASE-HERO-MYNAAANI` is `.ai/process/PHASE_INVENTORY_HERO_MYNAAANI.md`.
- `SRC-PREFLIGHT-HERO-MYNAAANI` is `.ai/process/PREFLIGHT_HERO_MYNAAANI.md`.
- `SRC-LESSONS-HERO-MYNAAANI` is `.ai/process/LESSONS_LEARNED_HERO_MYNAAANI.md`.
- `DEP-HERO-MYNAAANI-IMAGE` is `/home/hazbyn/Downloads/formynaani.png`.
- `CAP-HERO-LANDING-FULLPAGE` `uses_asset` `public/hero-mynaani.png`.
- `EVI-HERO-004-PREFLIGHT` is `PREFLIGHT_HERO_MYNAAANI.md` with `GO` status.
- `GAP-HERO-COPYRIGHT` notes the screenshot is a placeholder, not production-cleared.
- `EVI-HERO-004-BUILD` is `npm run type-check` and `npm run build` passing.
- `CAP-HERO-MYNAAANI` depends_on `public/hero-mynaani.png` and is implemented in `LandingPage.tsx`.
- `EVI-HERO-004-DEPLOY` is live bundle `https://noni-web.pages.dev/assets/index-DuqHZxup.js` and image `https://noni-web.pages.dev/hero-mynaani.png`.
- `CAP-HERO-MYNAAANI` status is `deployed`.

## HERO-006 high-resolution original image search (2026-08-27)

- `SRC-HERO-006-INTAKE` is `.ai/intake/2026-08-27-find-highres-mynaani-original.md`.
- `SRC-PHASE-HERO-ORIGINAL` is `.ai/process/PHASE_INVENTORY_HERO_ORIGINAL.md`.
- `SRC-PREFLIGHT-HERO-ORIGINAL` is `.ai/process/PREFLIGHT_HERO_ORIGINAL.md`.
- `SRC-FINDINGS-HERO-ORIGINAL` is `.ai/process/HERO_ORIGINAL_IMAGE_RESEARCH.md`.
- `EVI-HERO-006-DAM` is `https://dam.metlife.com/` and
  `https://metlifeglobal.brand-portal.adobe.com/.../photography`.
- `EVI-HERO-006-PORTAL` shows the original is behind MetLife Adobe Brand Portal.
- `CAP-HERO-ORIGINAL-RESEARCH` status is `completed` with no public URL.

## HERO-008 low-pressure hero CTA (2026-08-27)

- `SRC-HERO-008-INTAKE` is `.ai/intake/2026-08-27-hero-low-pressure-cta.md`.
- `SRC-PHASE-HERO-008` is `.ai/process/PHASE_INVENTORY_HERO_008.md`.
- `SRC-PREFLIGHT-HERO-008` is `.ai/process/PREFLIGHT_HERO_008.md`.
- `EVI-HERO-008-BUILD` is `npm run type-check` and `npm run build` passing.
- `EVI-HERO-008-DEPLOY` is GitHub Actions deploy `33112574993`.
- `CAP-HERO-008` status is `deployed`.

## PRICING-001 older-adult pricing research (2026-08-27)

- `SRC-PRICING-001-INTAKE` is `.ai/intake/2026-08-27-pricing-research-001.md`.
- `SRC-PRICING-001-PREFLIGHT` is `.ai/process/PREFLIGHT_PRICING_001.md`.
- `SRC-PRICING-001-PHASE` is `.ai/process/PHASE_INVENTORY_PRICING_001.md`.
- `EVI-PRICING-001-RESEARCH` is `.ai/process/PRICING_RESEARCH_001.md`.
- `DEC-PRICING-001` is recommendation: keep ADR 0021 one-time purchase, strengthen caregiver gift, optional reverse trial.
- `CAP-PRICING-001` status is `completed`.

## PRICING-001 ontology and traceability

- `ONTO-PRICING-001` is `.ai/process/PRICING_ONTOLOGY_001.md`.
- `SRC-AARP-2025` `evidenced_by` `EVI-PRICING-001`.
- `SRC-JAMR-2017` `evidenced_by` `EVI-PRICING-002`.
- `SRC-GERONTOL-2016` `evidenced_by` `EVI-PRICING-003`.
- `SRC-CHI-2024` `evidenced_by` `EVI-PRICING-004`.
- `SRC-KYLE-POYAR` `evidenced_by` `EVI-PRICING-005`.
- `SRC-LUMOSITY`, `SRC-DUOLINGO`, `SRC-TOOLRADAR-2026` `evidenced_by` `EVI-PRICING-006`.
- `SRC-GERAGOGY-2022` `evidenced_by` `EVI-PRICING-007`.
- `EVI-PRICING-001`, `EVI-PRICING-002`, `EVI-PRICING-007` `defines` `REQ-PRICING-001`.
- `EVI-PRICING-004` `defines` `REQ-PRICING-002`.
- `EVI-PRICING-003` `defines` `REQ-PRICING-003`.
- `EVI-PRICING-007`, `EVI-PRICING-004` `defines` `REQ-PRICING-004`.
- `SRC-ADR-0021` `defines` `REQ-PRICING-005` and `REQ-PRICING-006`.
- `SRC-ADR-0021` `defines` `REQ-PRICING-007`.
- `REQ-PRICING-001` `serves` `PERSONA-Learner-55Plus`.
- `REQ-PRICING-003` `serves` `PERSONA-Caregiver`.
- `REQ-PRICING-005` `part_of` `JOURNEY-FreeToPaid`.
- `REQ-PRICING-003` `part_of` `JOURNEY-GiftPurchase`.
- `CAP-Paywall` `implements` `REQ-PRICING-005` and `REQ-PRICING-006`.
- `CAP-GiftRedeem` `implements` `REQ-PRICING-003`.
- `CAP-Refund` `implements` `REQ-PRICING-007`.
- `CAP-ReverseTrial` `implements` `REQ-PRICING-004` and `US-PRICING-004`.
- `DEC-PRICING-001` `decides` `REQ-PRICING-001`, `REQ-PRICING-002`, `REQ-PRICING-004`, `REQ-PRICING-006`.
- `DEC-PRICING-002` `decides` `REQ-PRICING-004` (optional, future).
- `DEC-PRICING-003` `decides` `REQ-PRICING-002`.
- `DEC-PRICING-001`, `DEC-PRICING-002`, `DEC-PRICING-003` `owned_by` `OWNER-Product`.
- `CAP-Paywall`, `CAP-GiftRedeem`, `CAP-Refund`, `CAP-ReverseTrial` `owned_by` `OWNER-Engineering`.
- `ASM-PRICING-001` and `ASM-PRICING-002` are `assumes` on `DEC-PRICING-001`.
- `GAP-PRICING-001`, `GAP-PRICING-002`, `GAP-PRICING-003` are `has_gap` on `DEC-PRICING-001`.
