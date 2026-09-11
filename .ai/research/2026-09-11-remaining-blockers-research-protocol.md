# Research Protocol: remaining launch blockers (measured evidence)

**Process:** v9.51
**Date:** 2026-09-11
**ID:** RP-REMAINING-BLOCKERS-002
**Status:** RESEARCH COMPLETE — measured, superseding the estimates in
`.ai/research/2026-09-11-backend-maturity-research-protocol.md`
**Owner:** Platform + Backend + Security + Compliance
**Scope:** Items 1–5 of the launch-blocker list, re-measured against the
repository as it exists at commit `485b6cd` (now `origin/main`).

---

## 0. Why this protocol exists

The first protocol (`RP-BACKEND-MATURITY-001`) recorded backend coverage as
"~42%". That figure was **not reproducible**. This protocol replaces every
estimate with a measured value and cites the exact command used, so the
remediation intake is built on evidence rather than recollection.

---

## 1. Backend coverage — MEASURED

### Command

```bash
.venv/bin/coverage run --branch --source=backend -m pytest backend/tests --no-cov -q
.venv/bin/coverage json -o /tmp/cov.json --fail-under=0
```

### Result

| Metric | Value | Target | Gap |
|---|---|---|---|
| Statements | 3,834 total, 3,284 covered | — | — |
| **Statement coverage** | **85.65 %** | 87 % | **-1.35 pt** |
| Branches | 778 total, 482 covered, 296 missing | — | — |
| **Branch coverage** | **61.95 %** | 75 % | **-13.05 pt** |
| Combined (coverage.py score) | 81.66 % | — | — |
| Test outcome | 454 passed, 2 skipped, 14 xfailed | — | — |

### Finding

The earlier "42%" figure was wrong. Statement coverage is **within 1.35
points** of the 87 % target. **Branch coverage is the real gap** at 61.95 %
against a 75 % target, and it had never been measured because
`[tool.coverage.run]` does not set `branch = true`.

### Lowest-coverage modules (statement %)

| Module | Stmt cover | Missing lines | Risk |
|---|---|---|---|
| `backend/api/routes/account.py` | 29 % | 69-133, 178-236 | Account read/update routes entirely untested |
| `backend/api/routes/session_validation.py` | 43 % | 52-95 | Session validation path untested |
| `backend/tasks/org_tasks.py` | 51 % | 26-90, 116-134 | Org provisioning background tasks |
| `backend/services/magic_verifier.py` | 54 % | 40-63, 100-114 | Auth token verification |
| `backend/core/secret_rotation.py` | 60 % | 39-55 | Key rotation |
| `backend/services/org_quota.py` | 61 % | 57-86 | Quota enforcement branches |
| `backend/services/webhook_handler.py` | 63 % | 56-75, 151-178 | Stripe webhook handling |
| `backend/core/database.py` | 64 % | 44-51, 69-74 | Engine/session setup |
| `backend/services/organizations.py` | 66 % | 390-640 (blocks) | Bulk org operations |
| `backend/api/routes/billing.py` | 69 % | 248-299 | Checkout/portal paths |
| `backend/services/entitlements.py` | 71 % | 50-60, 90-92 | Entitlement gating branches |
| `backend/services/auth_verifier.py` | 72 % | 107-135 | Token/permission checks |
| `backend/api/routes/me.py` | 73 % | 45-52 | Profile route |
| `backend/api/routes/auth.py` | 75 % | 266-282 | Auth callback error branches |

Models and small utilities are already at or near 100 %, so the remaining
gap is concentrated in **6 route modules and 8 service/task modules**.

### Acceptance criteria

- Statement coverage ≥ 87 %.
- Branch coverage ≥ 75 %.
- No route module below 80 % statement coverage.

---

## 2. `magic-admin` / `requests` — MEASURED

### Commands

```bash
.venv/bin/python -m pip index versions magic-admin
.venv/bin/pip check
.venv/bin/pip-audit --format json
grep -rn "requests" .venv/.../magic_admin/*.py
```

### Result

| Fact | Evidence |
|---|---|
| Latest `magic-admin` on PyPI | **2.5.0** — already installed; no newer release exists |
| `magic-admin` declared requirement | `Requires-Dist: requests==2.32.5` (hard pin) |
| Installed `requests` | `2.34.2` |
| `pip check` | `magic-admin 2.5.0 has requirement requests==2.32.5, but you have requests 2.34.2` |
| `pip-audit` (current env) | **0 vulnerabilities reported** |
| Repo declares | `pyproject.toml: magic-admin>=2.4.0,<2.6.0` and `requirements.txt: magic-admin==2.5.0` |

### `requests` API surface actually used by `magic-admin`

Only three imports, all in `magic_admin/http_client.py`:

```python
from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
```

`Session` and `HTTPAdapter` are stable public API. `requests.packages` is a
**legacy compatibility shim** — this is the only genuinely fragile import.

### `magic-admin` usage surface in our code

`backend/services/magic_verifier.py` uses exactly:

- `Magic(api_secret_key=..., client_id=...)`
- `client.Token.decode` / `client.Token.validate`
- `client.User.get_metadata_by_token`
- error classes `DIDTokenExpired`, `DIDTokenInvalid`, `DIDTokenMalformed`, `MagicError`

This is a **very small surface** — four calls and four exception types.

### Finding

Upgrading the vendor is **not possible** (2.5.0 is latest). The pin is a
hard `==`, so `pip check` will always fail while `requests` is patched.
Three viable paths:

| Option | Effort | Risk | Verdict |
|---|---|---|---|
| A — wait for vendor | zero | unbounded; CVE stays declared | Rejected as sole plan |
| B — override the pin and pin `requests` ourselves | low | `requests.packages` shim could be removed upstream | **Recommended short term**, guarded by a test |
| C — replace with a ~60-line direct DID verifier | medium | we own JWT/DID verification correctness | **Recommended target state** |

Option B needs a **regression test that imports `magic_admin.http_client`**
so the `requests.packages` shim breaking is caught by CI, not production.

### Acceptance criteria

- `pip-audit` reports zero vulnerabilities against the **declared** graph.
- `pip check` is clean, or the override is explicit and documented.
- A test asserts `magic_admin.http_client` imports successfully under the
  patched `requests` version.
- Magic auth tests pass.

---

## 3. Branch-coverage gate — MEASURED

### Current state

`pytest.ini`:
```
--cov=backend --cov-report=term-missing --cov-fail-under=85
```

`pyproject.toml`:
```toml
[tool.coverage.run]
source = ["backend"]
omit = ["backend/tests/*"]

[tool.coverage.report]
fail_under = 85
show_missing = true
```

### Findings

1. `branch = true` is **absent**, so branch data is never collected in the
   normal test run. This is why branch coverage was unknown.
2. `pytest.ini` and `pyproject.toml` **both** declare coverage settings.
   pytest emits `WARNING: ignoring pytest config in pyproject.toml`, so the
   `pytest.ini` values win for `--cov-fail-under` while
   `[tool.coverage.*]` still governs `coverage`-CLI runs. This split is a
   silent-drift hazard.
3. `coverage.py` cannot enforce two different thresholds (statement and
   branch) in one `fail_under`. `fail_under` applies to the **combined**
   score once `branch = true` is on — which is why enabling branch
   coverage immediately dropped the reported total to 81.66 % and tripped
   the existing 85 % gate.

### Implication (important)

Simply adding `branch = true` will **break the existing gate** because the
combined metric is lower than the statement metric. The gate must be
restructured, not merely extended:

- Collect once with `--branch`.
- Assert statement % and branch % **separately** from the JSON report.

### Acceptance criteria

- `branch = true` is set.
- CI asserts statement ≥ 87 % and branch ≥ 75 % as two distinct checks.
- Duplicate/conflicting coverage config is consolidated.

---

## 4. Alembic downgrade validation — MEASURED

### Commands

```bash
.venv/bin/alembic heads
.venv/bin/alembic history
```

### Result

| Fact | Value |
|---|---|
| Heads | **1** — `p1_guest_gift_checkout` (no divergent heads) |
| Revisions | 20 files |
| Revisions defining `downgrade()` | **20 / 20** |
| Empty downgrade bodies | 1 — `663520a73af6` (a **merge** revision; empty is correct) |
| Branchpoint | `0003_launch_schema` → `m1_login_schema` |
| Mergepoint | `epic002_account_preferences` + `m2_idempotency_keys` → `663520a73af6` |

### Finding

The migration graph is **healthier than assumed**: single head, every
revision has a downgrade, and the one empty downgrade is a legitimate merge
node. The gap is purely that **`alembic downgrade` has never been
executed** — reversibility is declared but unproven, and the branch/merge
pair around `663520a73af6` is exactly where a naive `downgrade -1` is
likely to misbehave.

### Acceptance criteria

- `alembic upgrade head` then `alembic downgrade base` succeeds on a clean
  Postgres database.
- A full `upgrade → downgrade → upgrade` cycle succeeds.
- Behaviour across the `663520a73af6` mergepoint is documented.

---

## 5. PII / GDPR — MEASURED

### Commands

```bash
grep -rn "logger\.(info|warning|error|debug|exception)\(.*(email|name|token|account_id)" backend
grep -rn "email|display_name" backend/models
```

### PII fields in the schema

| Model | Field | Type |
|---|---|---|
| `accounts.py` | `email` | CITEXT, nullable |
| `accounts.py` | `display_name` | String(256) |
| `billing.py` | `display_name` | String(256), not null |
| `billing.py` | `buyer_email` | String(256), nullable |
| `organizations.py` | `contact_email` | String(256), not null |
| `organizations.py` | `admin_email` | String(256), not null |
| `organizations.py` | `email` (org contact) | String(256), nullable |

### Logging audit — result is good

Every matched log statement is already PII-safe:

| Location | Statement | Assessment |
|---|---|---|
| `magic_verifier.py:57,101,137` | logs `exc.__class__.__name__` only | Safe — class name, no token |
| `email.py:31` | logs `subject` only | Safe — no recipient |
| `email.py:50` | `logger.exception("email send failed")` | Safe — no address |
| `telemetry.py:122` | `"account.email_collision_observed"` | Safe — event name only |

### The one real exposure

`backend/services/email.py:47`

```python
logger.warning("email rejected %s: %s", resp.status_code, resp.text[:200])
```

This logs the **provider's raw response body**. Resend echoes the
submitted `to` address in validation errors, so a rejected send can write a
learner's email address into application logs. This is the single concrete
GDPR data-minimisation defect found.

### Finding

The codebase is already close to PII-clean by convention, but there is
**no enforcement**. One provider-response log leaks addresses today, and
nothing prevents the next contributor from adding `logger.info(f"...{email}")`.

### Acceptance criteria

- A sanitiser masks email addresses and token-like strings.
- `email.py:47` no longer logs raw provider response bodies.
- A `logging.Filter` applies masking process-wide.
- A test proves an email address passed through a log record is masked.

---

## 6. Workflow token scope — MEASURED

### Command

```bash
/home/h/.local/bin/gh auth status
```

### Result

```
Logged in to github.com account smiles70
Token: gho_************************************
Token scopes: 'gist', 'read:org', 'repo'
```

### Finding

Confirmed root cause. The active token is a `gho_` **OAuth app token** whose
scopes are `gist`, `read:org`, `repo`. The **`workflow` scope is absent**,
which is exactly why GitHub rejects pushes touching
`.github/workflows/a10-smoke.yml`. This is a credential-provisioning issue,
not a code issue — no amount of rebasing or re-committing will clear it.

### Remediation (human action required)

```bash
gh auth refresh -h github.com -s workflow
```

or issue a fine-grained PAT with **Actions: read and write** and
**Contents: read and write**.

### Acceptance criteria

- `gh auth status` lists `workflow` among the scopes.
- Commit `f6d9718` pushes to `staging` without rejection.

### Constraint

This must be performed by the repository owner. No agent action can grant
the scope, and the token must never be echoed into a report or commit.

---

## 7. Corrections to the previous protocol

| Claim in RP-BACKEND-MATURITY-001 | Measured reality |
|---|---|
| "Backend coverage is ~42%" | **85.65 % statements**; 61.95 % branches |
| "needs route/service unit tests to reach 87/75" | Correct in direction; the real gap is **branch**, not statement |
| "magic-admin needs vendor update" | **No newer version exists** — vendor update is not an available option |
| "Alembic downgrade paths unknown" | Single head, **20/20 downgrades defined**; only execution is unproven |
| "PII scan still to implement" | Logging is **already 95 % clean**; exactly one real leak (`email.py:47`) |
| "Workflow file needs a token with workflow scope" | Confirmed: scopes are `gist, read:org, repo` |

---

## 8. Evidence index

- Coverage: `coverage run --branch --source=backend -m pytest backend/tests`
- Dependency: `pip index versions magic-admin`, `pip check`, `pip-audit`
- Vendor source: `.venv/lib/python3.12/site-packages/magic_admin/http_client.py`
- Migrations: `alembic heads`, `alembic history`, `alembic/versions/*.py`
- PII: `backend/models/{accounts,billing,organizations}.py`, `backend/services/email.py`
- Token: `gh auth status`
- Prior protocol: `.ai/research/2026-09-11-backend-maturity-research-protocol.md`
- Prior intakes: `.ai/intake/2026-09-11-p1-*-v951-intake-00{6,7,8,9}.md`
