# Constraint Refinement — Noni Login Domain

**Date:** 2026-05-17
**Source:** `docs/audits/login-system-constraints-2026-05-17.md` +
`docs/audits/login-discovery-2026-05-17.md`.
**Mode:** traceability + sequencing + validation mapping. No new
constraints; no design.
**Frozen reference tag:** `login-constraints-v1`.

---

## PHASE 1 — CONSTRAINT TRACEABILITY MAP

Failure-mode IDs (F1–F10, FC1–FC6) and invariant violation IDs
reference the discovery audit.

### 1A — Build constraints

```
CONSTRAINT: B1 — Single auth-state owner
DERIVED FROM: F8, audit §17, I-G violation
PROTECTS AGAINST: chrome/body inconsistency, duplicate whoami requests,
                  FE-state divergence
VALIDATED BY: T-H2, T-B2

CONSTRAINT: B2 — One credential pipeline
DERIVED FROM: audit §1 (two interceptor install paths), F6, audit §8 race-2
PROTECTS AGAINST: wrong-token attachment after mode switch,
                  header-write collisions
VALIDATED BY: T-D1, T-D2

CONSTRAINT: B3 — Build/runtime provider symmetry
DERIVED FROM: audit Phase 11 two-element kills (a), F6
PROTECTS AGAINST: silent 401 storm from FE/BE provider mismatch
VALIDATED BY: T-D2

CONSTRAINT: B4 — No write effects on read endpoints
DERIVED FROM: audit §13, FC1 (commit-on-read first sight), I-B violation
PROTECTS AGAINST: side-effect amplification, hidden mutations,
                  parallel-caller races
VALIDATED BY: T-H3, T-A2

CONSTRAINT: B5 — Discriminated 401
DERIVED FROM: audit Phase 12 (401 collapses 7 causes), FC1, FC2,
              F1, F2, F4, I-A and I-J consequences
PROTECTS AGAINST: false signed-out, indistinguishable transient vs
                  definitive failures, sign-in loops
VALIDATED BY: T-B1, T-B3, T-E1, T-E2

CONSTRAINT: B6 — Disjoint sign-out
DERIVED FROM: audit §13 sign-out asymmetry, F7, F-G5, I-C violation
PROTECTS AGAINST: stale progress for next user, cross-provider token
                  leakage
VALIDATED BY: T-F2

CONSTRAINT: B7 — Deletion is terminal
DERIVED FROM: FC4, I-E violation, I6 violation
PROTECTS AGAINST: resurrection of deleted accounts via valid token
VALIDATED BY: T-G1

CONSTRAINT: B8 — One Clerk subject ↔ at most one account row
DERIVED FROM: FC3, audit §13 Race-B row, I-D violation, I5 violation
PROTECTS AGAINST: silent ownership transfer between identity-provider
                  subjects
VALIDATED BY: T-G2

CONSTRAINT: B9 — No unreachable view states
DERIVED FROM: audit §7 (oauth_finishing orphan), §15 I9 violation
PROTECTS AGAINST: dead states that can be entered but never exited
VALIDATED BY: T-C1, T-C2

CONSTRAINT: B10 — No diagnostic credential leakage
DERIVED FROM: audit Phase 1 (DIAG_AUTHZ_HEADER prints), F10
PROTECTS AGAINST: header/token prefix leakage to log aggregators
VALIDATED BY: T-H1

CONSTRAINT: B11 — No optional secrets on success path
DERIVED FROM: F2, audit Phase 11 single-element kills, C1 protection
PROTECTS AGAINST: critical-path collapse on missing optional config
VALIDATED BY: T-A3

CONSTRAINT: B12 — Schema-token compatibility
DERIVED FROM: audit Phase 14 (NOT NULL email vs Clerk default token),
              F2 chain, audit Phase 23 flaw #3
PROTECTS AGAINST: synchronous critical-path dependency on out-of-band
                  profile fetch
VALIDATED BY: T-A2, T-A3
```

### 1B — System invariants

```
CONSTRAINT: I-A — provider-signed-in + token-ready ⇒ no false 401
DERIVED FROM: FC1, F1, F2, F4, audit Phase 23 flaw #1
PROTECTS AGAINST: SIGNIN ↔ GATED_LOCKED oscillation, eviction on
                  transient backend failure
VALIDATED BY: T-B1, T-A1, T-E1

CONSTRAINT: I-B — read endpoints do not write
DERIVED FROM: audit Phase 13, FC1 first-sight commit
PROTECTS AGAINST: side-effect surprise, write amplification under read load
VALIDATED BY: T-H3

CONSTRAINT: I-C — sign-out is monotonic
DERIVED FROM: F6, F7, audit §13 asymmetric sign-out
PROTECTS AGAINST: post-signout residue
VALIDATED BY: T-F2, T-B2

CONSTRAINT: I-D — (subject → account) mapping is monotonic
DERIVED FROM: FC3, audit §13 Race B
PROTECTS AGAINST: silent ownership transfer, audit-trail gaps
VALIDATED BY: T-G2

CONSTRAINT: I-E — deleted row not returned by current-account lookup
DERIVED FROM: FC4, audit §15 I6
PROTECTS AGAINST: deleted-user resurrection
VALIDATED BY: T-G1

CONSTRAINT: I-F — progress scoped by authenticated account
DERIVED FROM: F7, audit Phase 21 row "I'm on lesson 5"
PROTECTS AGAINST: cross-user progress leakage on shared browsers
VALIDATED BY: T-F2

CONSTRAINT: I-G — no two components render contradictory signedIn
DERIVED FROM: F8, audit §17, audit §15 I7
PROTECTS AGAINST: chrome/body disagreement frames during boot or
                  post-signout
VALIDATED BY: T-B2, T-H2

CONSTRAINT: I-H — optional-dep failure does not cascade to existing users
DERIVED FROM: F4, audit Phase 16 blast radius
PROTECTS AGAINST: optional sub-dependency failure denying service
VALIDATED BY: T-E2, T-A3

CONSTRAINT: I-I — no auto-loop on deterministic failure
DERIVED FROM: FC1, audit Phase 7 documented loop, audit §15 I9
PROTECTS AGAINST: unbounded retry, SIGNIN ↔ GATED_LOCKED ping-pong
VALIDATED BY: T-C3, T-E1

CONSTRAINT: I-J — auth resolution before auth-dependent render
DERIVED FROM: audit §8 timing facts, audit §6 BOOT_UNKNOWN handling, F-G4
PROTECTS AGAINST: PendingBanner/SignIn flicker, decisions on unresolved
                  state
VALIDATED BY: T-D1, T-A1
```

### 1C — Temporal guarantees

```
CONSTRAINT: T1 — hydration before decision
DERIVED FROM: audit §8 timing facts, I-J
VALIDATED BY: T-D1, T-A1

CONSTRAINT: T2 — interceptor before request
DERIVED FROM: audit §8 race 1
VALIDATED BY: T-D1

CONSTRAINT: T3 — token before whoami
DERIVED FROM: ClerkAuthSync historical bug, FC1 prevention layer
VALIDATED BY: T-D1, T-A1

CONSTRAINT: T4 — provider parity before traffic
DERIVED FROM: audit Phase 11 two-element kill (a), F6
VALIDATED BY: T-D2

CONSTRAINT: T5 — sign-out completion before re-entry
DERIVED FROM: F6, F7, audit §13
VALIDATED BY: T-F2

CONSTRAINT: T6 — account materialization idempotent + non-blocking on read
DERIVED FROM: audit Phase 13, FC1, B4 derivation
VALIDATED BY: T-A3, T-H3

CONSTRAINT: T7 — one auth resolution per boot
DERIVED FROM: F8, audit §17 N+1 whoami
VALIDATED BY: T-H2
```

### 1D — Recovery rules (R1–R8) and 1E — Collapse-prevention (C1–C5)

(See full rules in §9 / §10 of constraint model. Mapping summary:)

```
R1 → T-B1, T-B3
R2 → T-C3, T-E1
R3 → T-B1, T-E1, T-F3
R4 → T-B3
R5 → T-E2
R6 → T-E3
R7 → T-C3, T-E1, T-E2
R8 → T-F2

C1 → T-A3
C2 → T-E1, T-E2
C3 → T-E2, T-A3
C4 → T-C1
C5 → T-A3, T-E2
```

### 1F — Forbidden-pattern coverage

```
F-A1 → B1, I-A           → T-B1, T-H2
F-A2 → B4, I-B           → T-H3
F-A3 → B5, I-A           → T-B1, T-B3
F-A4 → T1, T2, T3, I-J   → T-D1
F-A5 → B1, T7            → T-H2
F-A6 → B3, T4            → T-D2
F-A7 → B10               → T-H1
F-A8 → B7, I-E           → T-G1

F-G1 → I-A, R3           → T-A1, T-A2, T-B1
F-G2 → B6, I-F           → T-F2
F-G3 → I-A, R3           → T-F3
F-G4 → I-J               → T-D1
F-G5 → B6, R8            → T-F2
```

---

## PHASE 2 — INVARIANT COVERAGE VALIDATION

| Invariant | Tests covering | Status |
|---|---|---|
| I-A | T-A1, T-B1, T-E1 | ✅ |
| I-B | T-H3 | ✅ |
| I-C | T-B2, T-F2 | ✅ |
| I-D | T-G2 | ✅ |
| I-E | T-G1 | ✅ |
| I-F | T-F2 | ✅ |
| I-G | T-B2, T-H2 | ✅ |
| I-H | T-E2, T-A3 | ✅ |
| I-I | T-C3, T-E1 | ✅ |
| I-J | T-D1, T-A1 | ✅ |

**VERIFIED:** all 10. **UNVERIFIED:** none.

---

## PHASE 3 — ACCEPTANCE TEST COVERAGE MATRIX

| Test | Constraints | Invariants | Failure modes prevented |
|---|---|---|---|
| T-A1 | B1, B3, B11, B12, T1, T3, T7, R3 | I-A, I-G, I-J | F1 (existing), F8, FC1 (existing) |
| T-A2 | B4, B5, B12, T6 | I-A, I-B | FC1 (new), F2 |
| T-A3 | B11, B12, C1, C5, R5 | I-H | F2, F4 |
| T-B1 | B5, R1, R3 | I-A | F1, F3, FC1, FC2 |
| T-B2 | B1, B6 | I-C, I-G | F8, FC5 |
| T-B3 | B5, R1, R4 | I-A, I-I | definitive 401 differentiation |
| T-C1 | B9, C4 | (none direct) | F9, audit §7 dead-end |
| T-C2 | B9 | (none direct) | F9 |
| T-C3 | I-I, R2, R7 | I-I | FC1 oscillation |
| T-D1 | B2, T1, T2, T3 | I-J | audit §8 race-1, race-2 |
| T-D2 | B3, T4 | (none direct) | F6 mismatch class |
| T-E1 | B5, C2, R3, R7 | I-A, I-I | F1, F3 |
| T-E2 | C2, C3, C5, R5 | I-H | F4 |
| T-E3 | R6 | (boundary §11.3) | DB-blast-radius |
| T-F1 | progression continuity §5.2 | I-F implicitly | progression-reset class |
| T-F2 | B6, I-C, I-F, R8 | I-C, I-F | F7, FC5 |
| T-F3 | R3 | I-A | F3 |
| T-G1 | B7, I-E | I-E | FC4 |
| T-G2 | B8, I-D | I-D | FC3 |
| T-H1 | B10 | (none direct) | F10 |
| T-H2 | B1, T7 | I-G | F8, audit §17 |
| T-H3 | B4, I-B, T6 | I-B | FC1 commit-on-read |

### Coverage summary

- **Redundant tests:** none.
- **Constraints validated by exactly one test:** B7→T-G1, B8→T-G2,
  B10→T-H1, T4→T-D2, R6→T-E3, R8→T-F2.
- **Indirectly validated (recommendation: explicit assertions inside
  existing tests):** T5 (T-F2), R2 (T-C3), C4 (T-C1).

---

## PHASE 4 — CRITICAL PATH DEPENDENCY GRAPH

```
LANDING_OUT  →  SIGNIN  →  SUCCESS_STATE  →  CURRICULUM(entry-point)
```

### Aggregate critical-path constraint set

```
{ T1, T2, T3, T4, T6, T7,
  B2, B3, B5, B6, B7, B9, B11, B12,
  C1, C2, C3, C4, C5,
  R1, R3, R4, R5, R6,
  I-A, I-E, I-F, I-G, I-H, I-J }
```

Constraints not on the critical path (still required globally): B1, B4,
B8, B10, I-B, I-C, I-D, I-I, R2, R7, R8, T5.

### Step-by-step

```
STEP 1: LANDING_OUT (initial)
  Dependencies: public landing envelope; provider SDK hydration
  Constraints: I-J, T1, T7, R6
  Failure points: SDK hydration delay
  Protections: T1, I-J ensure deterministic loading state

STEP 2: LANDING_OUT → SIGNIN
  Dependencies: view-state owner; public envelope for SIGNIN
  Constraints: B9, C4
  Failure points: none

STEP 3: SIGNIN → SUCCESS_STATE
  Dependencies: provider SDK signed-in; non-null token; interceptor
                installed; backend reachable; JWKS reachable or cached;
                account row exists OR materializable via critical-only deps
  Constraints: T1, T2, T3, B2, B3+T4, B5+R1, I-A+R3,
               C1, C2, C3, C5, B11, B12, T6
  Failure points & protections:
    JWKS outage           → I-H, R5, B5
    Token rejected        → B5, R4
    Token expired         → R3
    Profile lookup needed → B11, B12, C1, C3 forbid this dependency
    Account row deleted   → B7, I-E
    Account row missing   → T6 (non-blocking)
    DB unavailable        → R6

STEP 4: SUCCESS_STATE → CURRICULUM(entry)
  Dependencies: persisted progress for authenticated account
  Constraints: I-F, B6, I-G, F-G1, F-G3
  Failure points: shared-browser progress; mid-load whoami flicker
  Protections: B6 + I-F; I-J + T7
```

---

## PHASE 5 — EXECUTION ORDER

### Stage 1 — BLOCKING

```
1.1  B12  schema-token compatibility
1.2  B3   build/runtime provider symmetry
1.3  T4   provider parity before traffic
1.4  B11  no optional secrets on success path
1.5  B7   deletion terminal (schema contract)
1.6  B8   one subject ↔ one row
1.7  I-D  subject→row monotonic
1.8  I-E  deleted row not returned by lookup
```

### Stage 2 — FOUNDATIONAL

```
2.1   B1   single auth-state owner
2.2   B2   one credential pipeline
2.3   T1   hydration before decision
2.4   T2   interceptor before request
2.5   T3   token before whoami
2.6   T7   one auth resolution per boot
2.7   {B4, T6}  joint unit (no write-on-read; non-blocking materialization)
2.8   B5   discriminated 401
2.9   R1   discriminated reason on failure
2.10  I-A, I-B, I-G, I-J  (runtime guarantees)
2.11  B10  no diagnostic credential leakage
```

### Stage 3 — STABILIZATION

```
3.1   C3   verify / profile / create separable
3.2   C1   no single optional config gates path
3.3   C5   existing-user critical path with optional deps down
3.4   R5   optional-dep failure does not cascade
3.5   R3, R4  transient vs definitive failure handling
3.6   R2, R7  no auto re-issue; bounded convergence
3.7   C2   no single network dep collapses app
3.8   R6   route isolation
3.9   B6, T5   disjoint sign-out, completion before re-entry
3.10  I-C, I-H, I-I  (runtime guarantees)
3.11  B9, C4   no unreachable views, every critical state has exit
3.12  R8       recovery without dev escape hatches
```

### Stage 4 — EXPERIENCE

```
4.1  I-F  progress scoped by account
4.2  §5.1 learning entry guarantee
4.3  §5.2 progression guarantees
4.4  §5.3 experience consistency
4.5  F-G1..F-G5 forbidden patterns asserted
4.6  §6.1, §6.2 interaction + navigation guarantees
```

---

## PHASE 6 — CONSTRAINT DEPENDENCY ANALYSIS

```
Stage 1:
  B12 ← {}
  B3  ← {}
  T4  ← {B3}
  B11 ← {B12}
  B7  ← {B12}
  B8  ← {B12}
  I-D ← {B8}
  I-E ← {B7}

Stage 2:
  B1  ← {}
  B2  ← {B3, T4}
  B4  ← {B12, T6}
  T6  ← {B4, B11, B12}      # joint with B4
  T1  ← {B1}
  T2  ← {B2}
  T3  ← {T1, T2}
  T7  ← {B1, T1}
  I-A ← {B5, T3, T6}
  I-B ← {B4, T6}
  I-G ← {B1, T7}
  I-J ← {T1, B1}
  B5  ← {B12, B11}
  R1  ← {B5}
  B10 ← {}

Stage 3:
  B6  ← {B1, I-C}
  T5  ← {B6}
  R2  ← {B5, I-I}
  R3  ← {B5, I-A}
  R4  ← {B5, I-I}
  R5  ← {B11, C3}
  R6  ← {C3}
  R7  ← {R2, R4}
  R8  ← {B6}
  C1  ← {B11}
  C2  ← {C3, R5}
  C3  ← {B4, T6}
  C4  ← {B9}
  C5  ← {C1, C3, R5, I-H}
  I-C ← {B6}
  I-H ← {C3, R5}
  I-I ← {R2, R4}
  B9  ← {}

Stage 4:
  F-G1, F-G3 ← {I-A, R3}
  F-G2       ← {B6, I-F}
  F-G4       ← {I-J}
  F-G5       ← {B6, R8}
  I-F        ← {B6}
  §5.1, §5.2 ← {I-A, I-F, R3}
  §5.3       ← {I-G, I-F}
  §6.1       ← {B5, R1}
  §6.2       ← {B9, C4}
```

### Cycle check

- **B4 ↔ T6** is a co-defined satisfaction unit (clarification, not a
  cycle). Implement atomically.
- No other cycles detected.

### Hidden ordering constraints surfaced

1. **B12 must precede B5.** Discriminated-reason vocabulary depends on
   the schema decision.
2. **B11 must precede T6.** "Materialization non-blocking on read"
   presupposes nothing the read needs is locked behind an optional
   secret.
3. **B9 must precede §6.2.** Navigation guarantees about reachable
   gated routes assume no unreachable views elsewhere.
4. **B6 + I-C must precede F-G2 and F-G5.**

---

## PHASE 7 — FAILURE ELIMINATION MATRIX

```
F1   → B5, R3, R5, I-A, I-H, C2          partial
F2   → B11, B12, C1, C3, C5              direct
F3   → R3, I-A                           partial
F4   → I-H, R5, C2, C3, C5               partial-to-direct
F5   → B8, I-D                           direct
F6   → B6, I-C, T5, B3, T4               direct
F7   → B6, I-F                           direct
F8   → B1, T7, I-G                       direct
F9   → B9, C4                            direct
F10  → B10                               direct

FC1  → B5, B11, B12, T6, R2, I-A, I-I, T3   direct
FC2  → B5, I-H, C2, R5                   partial
FC3  → B8, I-D                           direct
FC4  → B7, I-E                           direct
FC5  → B6, I-F                           direct
FC6  → B1, T2, T7, I-G                   direct
```

**Aggregate:** 15 failure modes; 12 directly eliminated, 3 partial
(F1, F3, FC2 — all rooted in external-network properties).

---

## PHASE 8 — RISK-ALIGNED EXECUTION CHECKS

```
E1 (email NOT NULL migration)
  AFFECTED: B12, B11, B5; I-A
  GATE: schema applied + backfill verified; T-A2, T-A3 pass before
        any frontend change

E2 (commit-on-read removal)
  AFFECTED: B4, T6, C3; I-B
  GATE: T-H3 passes; explicit materialization event exists; FE switched
        before write code stripped

E3 (FE/BE provider parity enforcement)
  AFFECTED: B3, T4
  GATE: T-D2 passes in CI with deliberate mismatch

E4 (discriminated 401 wire format)
  AFFECTED: B5, R1; I-A, I-I
  GATE: FE tolerant of both shapes; T-B1, T-B3 pass on each shape

E5 (NavBar whoami removal)
  AFFECTED: B1, T7; I-G
  GATE: T-H2 passes; whoami request-rate baseline re-captured

E6 (sign-out collapse)
  AFFECTED: B6; I-C
  GATE: T-F2 passes in BOTH mock and clerk CI matrices

E7 (Race B removal)
  AFFECTED: B8; I-D
  GATE: T-G2 passes; admin runbook documents legitimate
        email-reassignment

E8 (deletion semantics across service boundary)
  AFFECTED: B7; I-E
  GATE: T-G1 passes; deletion ↔ provider-session interaction documented

E9 (frontend rebuild discipline)
  AFFECTED: B3, T4
  GATE: deploy runbook updated; CI builds on every VITE_AUTH_PROVIDER
        change

E10 (telemetry blind spots)
  AFFECTED: B5, B8, B4; I-A, I-D, I-F
  GATE: telemetry surfaces in place BEFORE redesign code lands
        (precondition for measuring success of E1–E8)
```

---

## PHASE 9 — FINAL SYNTHESIS

### 9.1 Traceability graph

```
                      ┌──────────────────────────────────────────────┐
                      │                FAILURE MODES                 │
                      │  F1..F10  FC1..FC6                           │
                      └─────────────┬─────────────────┬──────────────┘
                                    │                 │
                                    ▼                 ▼
   ┌───────────────────────────────────┐   ┌───────────────────────────┐
   │            CONSTRAINTS            │   │       INVARIANTS          │
   │  B1..B12, T1..T7, R1..R8,         │◀─▶│  I-A..I-J                 │
   │  C1..C5, F-A1..F-A8, F-G1..F-G5   │   │                           │
   └─────────────┬─────────────────────┘   └────────────┬──────────────┘
                 │                                      │
                 ▼                                      ▼
            ┌──────────────────────────────────────────────┐
            │              ACCEPTANCE TESTS                │
            │  T-A1..T-A3  T-B1..T-B3  T-C1..T-C3          │
            │  T-D1..T-D2  T-E1..T-E3  T-F1..T-F3          │
            │  T-G1..T-G2  T-H1..T-H3                      │
            └──────────────────────────────────────────────┘
```

### 9.2 Execution order summary

```
Stage 1: BLOCKING        (schema/contract/identity decisions)
Stage 2: FOUNDATIONAL    (auth consistency, state ownership, timing)
Stage 3: STABILIZATION   (loops, races, isolation)
Stage 4: EXPERIENCE      (geragogy, navigation, UX integrity)
```

### 9.3 Coverage report

- **Fully validated:** ✅ B1, B3, B4, B5, B6, B7, B8, B9, B10, B11,
  B12, T1, T2, T3, T4, T6, R1, R3, R4, R5, R6, C1, C2, C3, C5, I-A,
  I-B, I-C, I-D, I-E, I-F, I-G, I-H, I-I, I-J.
- **Partially validated (recommend explicit assertion):** ⚠️ B2, T5,
  T7, R2, R7, R8, C4.
- **Not validated:** ❌ none.

### 9.4 Readiness assessment for redesign

**Verdict:** the constraint model is **sufficient for deterministic
redesign**, with these qualifications:

1. **B4 ↔ T6** is a co-defined satisfaction unit; redesign must
   implement them atomically.
2. **Partial-validation items** are acceptable to start; redesign
   acceptance must convert ⚠️ to ✅ via explicit assertions in the
   linked tests.

**Ambiguity items (scope questions, not constraint omissions):**

- **B7 deletion semantics across service boundary:** explicit
  re-creation flow scope is a redesign decision.
- **B12 schema-token compatibility migration sequence:** schema →
  backfill → constraint relaxation → app change. Order is binding.
- **B5 discriminated reason vocabulary:** exact codes are a redesign
  decision.

**Conclusion:** full failure-mode coverage (15/15), full invariant
coverage (10/10), full constraint→test traceability (no orphans).
Stage ordering eliminates known cyclic risks. **Phase 2 redesign may
proceed.**

---

# END OF CONSTRAINT REFINEMENT
