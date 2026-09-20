# Assessment — `agents-error-handling-patterns.zip` (`error-handling-patterns` SKILL.md)

**Date:** 2026-09-15
**Intake:** `.ai/intake/2026-09-15-p3-error-handling-skill-assessment.md`
**Artifact:** `/home/h/Downloads/agents-error-handling-patterns.zip`
(5,903 B → single `SKILL.md`, 641 lines, extracted to `/tmp/agents-eh/`)

---

## 1. What it is

A generic, cross-language error-handling playbook in Devin/Claude-skill
format. Four sections: error philosophies (exceptions vs Result types),
language patterns (Python, TypeScript, Rust, Go), universal patterns
(circuit breaker, error aggregation, graceful degradation), and best
practices/pitfalls. Written competently — idioms are correct, code is
illustrative-quality, organization is clean. Provenance is consistent
with generated/marketplace skill packs (skills.sh-style): one file, no
author, no tests, broad scope.

## 2. Quality findings

### Correctness issues found on read-through

1. **Python retry decorator loses context** — re-raises
   `last_exception` on final failure; intermediate tracebacks discarded;
   no jitter, no logging hook. Acceptable as illustration, unsafe to
   copy verbatim.
2. **Circuit breaker is not thread-safe** — mutable counters checked
   then mutated with no lock; `call()` raises a bare `Exception` instead
   of a typed `CircuitOpenError`. Demo-grade.
3. **Fallback helper silently swallows** — `try_function` catches bare
   `Exception` and returns `None`, which the skill itself lists as a
   pitfall ("Don't swallow errors") three sections later.
4. **`get_exchange_rate` chain is broken Python** — `or` between
   `try_function` results conflates falsy-but-valid `0.0` rates with
   failure. Subtle bug in a "best practice" example.
5. **TS `Result` chaining example is fine** but the file mixes
   philosophies (exceptions AND Result types) without guidance on where
   the boundary belongs — the one design question a consumer actually
   needs answered.
6. Rust/Go sections (~30% of file) are dead weight for this stack.

### Dead references

Footer advertises 6 companion files — `references/exception-hierarchy-
design.md`, `references/error-recovery-strategies.md`,
`references/async-error-handling.md`, `assets/error-handling-checklist.
md`, `assets/error-message-guide.md`, `scripts/error-analyzer.py` —
**none are in the zip.** Adopting as-is ships a skill with 6 dangling
pointers, which is worse than no skill.

## 3. Fit vs this codebase (grep-verified)

| Skill claims to provide | Repo already has |
|---|---|
| Custom exception hierarchy (Python) | Flat per-service exceptions: `GiftClaimError`, `WebhookVerificationError`, `AuthError` — plus a **documented wire contract** (`{error:{code,message}}` auth envelope + `envelope_id` UI envelope, enforced by `@app.exception_handler(HTTPException)` in `main.py:300`) |
| Retry w/ exponential backoff | Celery task retries (`email_tasks`, `webhook_tasks`, `telemetry_tasks`) + `frontend/src/api/client.ts` retry |
| Circuit breaker | `backend/app/circuit_breaker_metrics.py` exists |
| Graceful degradation | `with_fallback`-equivalent patterns in `api/client.ts`, `lib/progress.ts` |
| React error handling | `ErrorBoundary.tsx` + `OnboardingErrorBoundary.tsx` |
| Error taxonomy for CI gates | `.devin/skills/error-taxonomy/` — different problem (gate classification), already solved |

**Gap analysis (where the skill adds real value):**

- **Exception hierarchy** — repo exceptions are flat; the skill's
  `ApplicationError(code, details)` base-class pattern would unify
  `AuthError`/`GiftClaimError`/`WebhookVerificationError` under the
  existing wire envelope. Genuine, if modest, improvement.
- **TS `Result<T,E>` type** — frontend uses try/catch everywhere;
  a Result type could tighten `api/client.ts` — but that's a
  convention change needing its own intake.
- **Reference doc for contributors** — as reading material for
  "how we think about errors," trimmed to Python+TS.

**Overlap check vs `error-taxonomy`:** no functional collision —
`error-taxonomy` routes *CI gate failures*; this skill is *application
code* patterns. But two `error-*` skills will confuse trigger matching;
if adopted, rename to `app-error-patterns` or similar and sharpen the
`description:` trigger.

## 4. Options & decision matrix

| Option | Effort | Value | Risk | Verdict |
|---|---|---|---|---|
| A. Install as-is into `.devin/skills/` | Zero | Low | Ships 6 dead refs + demo-grade code an agent may copy verbatim | Reject |
| B. **Trim + localize**: keep Python+TS sections, align to our envelope/exceptions, drop Rust/Go, delete dead refs, rename `app-error-patterns` | ~1-2h | Moderate | Low — reviewed content only | **SELECT** |
| C. Reject entirely | Zero | None | Loses the two genuine gaps (hierarchy unification, Result type) | Reject |
| D. Merge into `error-taxonomy` | Medium | Moderate | Dilutes a working, focused skill | Reject |

**Recommendation: B — adopt trimmed.** Confidence: Medium-High.
The artifact is a decent reference skeleton whose value is realized
only after localizing to the repo's actual error contract; as shipped
it is not adoption-grade.

### Proposed trimmed content

1. `SKILL.md` frontmatter: `name: app-error-patterns`,
   `description:` scoped to "implementing error handling in backend
   services or frontend API/components" (no collision with
   `error-taxonomy` triggers).
2. Python section → rewrite hierarchy example to subclass a proposed
   `NoniError(code, http_status, details)` matching the existing
   `{error:{code,message}}` envelope; reference `main.py:300` handler.
3. TS section → keep `Result<T,E>` + custom error classes; add note
   that current convention is try/catch + envelope codes and any
   migration needs an intake.
4. Keep circuit-breaker *concept* only, pointing at
   `backend/app/circuit_breaker_metrics.py` as the repo implementation.
5. Delete: Rust, Go, dead references, `try_function` swallow pattern,
   the buggy `get_exchange_rate` chain.
6. Hardening notes appended to retry/circuit-breaker examples
   (typed exceptions, jitter, thread-safety).

## 5. Process notes

- Zip lives in `~/Downloads` — **do not commit the zip or the raw
  SKILL.md verbatim**; the deliverable (if approved) is a new file
  authored at `.devin/skills/app-error-patterns/SKILL.md`.
- Adoption is a `.devin/skills/` write — requires user go-ahead per
  intake scope ("assessment only").
- No journey-loop, landing-page, or deploy-gate surfaces involved.

## 6. User input needed

1. Approve Option B (trimmed adoption as `app-error-patterns`)?
2. Or defer — keep the zip as reference-only, no skill install?
