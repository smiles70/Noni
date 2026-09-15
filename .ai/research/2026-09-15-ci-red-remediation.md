# Research memo — CI red on `main`: Trivy OS-CVE remediation, ruff lint, corrupt a10-smoke workflow

**Date:** 2026-09-15
**Intake:** `.ai/intake/2026-09-15-p1-ci-red-main.md`
**Research questions:**
1. What is the best-in-class remediation for fixable OS-level CVEs in a
   `python:3.12-slim` (Debian 13/trixie) image failing a Trivy
   `CRITICAL,HIGH` + `ignore-unfixed` + `exit-code:1` gate?
2. How should the two `F401` ruff findings be cleared and prevented?
3. Repair or remove the corrupt `a10-smoke.yml` — and how do teams
   prevent broken workflow files reaching `main`?

---

## 1. Facts established from the codebase and CI logs

- `CI` run `35023135102` (main @ `f73ca68`): `backend` job fails at
  `Lint (ruff)` — F401 `FeatureFlags` (`backend/app/main.py:43`) and
  F401 `pytest` (`backend/tests/test_feature_flags.py:5`).
- `container-scan` job builds `noni-api:scan` from the **repo-root**
  `Dockerfile` (`docker build -t noni-api:scan -f Dockerfile .`) and
  fails Trivy with 12 findings (3 CRITICAL, 9 HIGH), all OS packages,
  all status `fixed`: perl-base (7 CVEs incl. CRITICAL CVE-2026-13221),
  libpcre2-8-0 (2), libsqlite3-0 (2), gzip (1).
- A second step scans `noni-frontend:scan` (`frontend/Dockerfile`,
  `nginx:1.29-alpine`) — did not fail.
- Debian security tracker confirms CVE-2026-13221 fixed in trixie at
  `5.40.1-6+deb13u1` — matches Trivy's "fixed" column exactly; the fix
  is a normal `apt-get upgrade` away (verified source S-13).
- `backend/Dockerfile` and root `Dockerfile` both use
  `python:3.12-slim` with near-identical two-stage layouts; both run
  `apt-get install` but **neither runs `apt-get upgrade`** — the exact
  root cause documented in source S-06.
- Railway deploys via `railway up` (no explicit Dockerfile flag);
  Railway builds from the repo root → root `Dockerfile` is what ships.
- `a10-smoke.yml` is committed but **invalid YAML**: line 1 starts
  mid-step, `name:` is glued to a `run:` line (`python3-devname:`).
  Corruption introduced by `69d7a14` ("Add system dependencies
  installation step"); the pre-corruption version is `d21820c`.
  GitHub rejects it at parse → zero-duration failure, zero logs.
- `.github/workflows/ci.yml` is locally modified (site-checker block);
  uncommitted, belongs to the human — must not be staged.

## 2. Source table

| # | Source | Author/Org | Date | Type | Verified |
|---|--------|-----------|------|------|----------|
| S-01 | github.com/aquasecurity/trivy — `docs/guide/configuration/others.md` (exit-code, ignore-unfixed, exit-on-eol) | Aqua Security | current | Vendor docs | webfetch/search |
| S-02 | github.com/aquasecurity/trivy-action README (severity/exit-code/ignore-unfixed inputs; SARIF option) | Aqua Security | v0.36.0 | Vendor docs | search |
| S-03 | github.com/docker-library/faq README — "Why does my security scanner show that an image has CVEs?" | Docker Official Images maintainers | current | Primary/official | webfetch |
| S-04 | github.com/docker-library/python issue #1120 — trixie base CVEs, rebuild policy | docker-library maintainers | 2026 | Primary/issue | search |
| S-05 | github.com/docker-library/official-images SECURITY.md | docker-library | e115ba1 | Primary/official | search |
| S-06 | github.com/agentic-community/mcp-gateway-registry issue #1061 — glibc CVE in `python:3.14-slim`, `apt-get upgrade` remediation, CIS-aligned | AWS agentic-community project | 2026-05-18 | Primary/issue | webfetch |
| S-07 | docs.docker.com/build/building/best-practices — rebuild often, `--pull`, `--no-cache`, pin digests | Docker Inc. | current | Top-tier docs | webfetch |
| S-08 | docs.docker.com/build/policies/validate-images — require digest references (Rego policy) | Docker Inc. | current | Top-tier docs | search |
| S-09 | github.com/GoogleContainerTools/distroless README — no shell/pkg-mgr, scanner signal-to-noise | Google | current | FAANG (Google) | webfetch |
| S-10 | bretfisher.com/blog/silent-rebuilds — image CVE rot; daily rebuilds vs upstream digest churn | Bret Fisher (Docker Captain) | 2025-2026 | Industry ops | search |
| S-11 | Shu, Gu, Enck — *A Study of Security Vulnerabilities on Docker Hub*, ACM CODASPY'17 (enck.org/pubs/shu-codaspy17.pdf) — ~180 vulns/image avg, parent→child propagation | NCSU | 2017 | Academic | webfetch (PDF) |
| S-12 | arXiv:2608.02669 — ChimangoScan: 96.3% of top-exposure images carry vulns; single-scanner counts are tool artifacts (2.7% tri-scanner agreement) | Kapelinski, Machado, Kreutz | 2026-08 | Academic | webfetch |
| S-13 | security-tracker.debian.org/tracker/CVE-2026-13221 — perl regex CVE, fixed trixie `5.40.1-6+deb13u1` | Debian Security Team | current | Primary/ops | webfetch |
| S-14 | Gholami, Khazaei, Bezemer — *Should you Upgrade Official Docker Hub Images in Production?* ICSE-NIER'21, doi:10.1109/ICSE-NIER52604.2021.00029 | York University | 2021 | Academic | search (DOI) |
| S-15 | *Dr. Docker / DITector* — ACM AsiaCCS'25, doi:10.1145/3696410.3714653 — 93.7% of images contain known vulns | Zhejiang Univ. et al. | 2025 | Academic | search (DOI) |
| S-16 | You, Kim, Shin — *Revisiting Security Landscape of Docker Hub Container Images*, J-KICS 47(8), DOI 10.7840/kics.2022.47.8.1231 — vulns patched ~3 days post-disclosure; propagation costly | KICS | 2022 | Academic | search (DOI) |
| S-17 | github.com/rhysd/actionlint — static checker for workflow files; CI/pre-commit integration | rhysd | current | Industry tool | webfetch |
| S-18 | docs.github.com — Workflow syntax for GitHub Actions | GitHub (Microsoft) | current | FAANG (MSFT) | search |
| S-19 | github.com/dependabot/dependabot-core PR #14071 — `docker_pin_digests` experiment | Dependabot/GitHub | 2026 | FAANG (GitHub) | search |
| S-20 | learn.microsoft.com — Dependabot + Copacetic container patching quickstart | Microsoft Azure | current | FAANG (MSFT) | search |
| S-21 | snyk.io/test/docker/python:slim — live vuln report (Debian 13) | Snyk | current | Industry/sec | search |
| S-22 | images.latio.com — base-image vuln comparison: `python:3.12-slim` 155 total/29 fixable; distroless 136/21 | Latio | 2026-07 | Industry data | search |
| S-23 | latchkey.dev — "Invalid workflow file": parse rejected before jobs run; actionlint prevention | Latchkey | current | Discussion/howto | search |
| S-24 | github.com/docker-library/faq issue #28 — Debian images rebuilt ≥monthly, earlier for critical need | docker-library | 2023 | Primary/issue | search |
| S-25 | kubethings.com — Trivy overwhelming by default; `--ignore-unfixed`, CVSS context | KubeThings | 2025 | Discussion | search |

Balance: FAANG/top-tier ≥5 (S-07, S-08, S-09, S-18, S-19, S-20),
academic ≥5 (S-11, S-12, S-14, S-15, S-16), industry/ops ≥5 (S-01,
S-02, S-10, S-13, S-17, S-21, S-22), discussion ≤5 (S-23, S-25,
issue-tracker primaries S-04/S-06/S-24).

## 3. Synthesis

**The OS-CVE class is well understood.** Official-image CVEs fall into
three buckets (S-03): (a) fixed upstream — actionable, our case;
(b) unfixed/won't-fix — noise `ignore-unfixed` already suppresses;
(c) false positives from backporting. Our scan shows all 12 in bucket
(a) — every finding has a fixed Debian package. This is the one bucket
where "just rebuild/upgrade" is the correct, complete answer.

**Why the image is stale:** Docker builds a snapshot (S-07). Our
Dockerfiles `apt-get install` new packages but never `apt-get upgrade`
the baked-in ones (S-06 documents the identical root cause on
`python:3.14-slim` and the identical fix). Debian trixie published
point-release fixes (S-13); the base image rebuilt recently enough to
be behind on them (S-04, S-24).

**Precedent for the fix:** mcp-gateway-registry patched eight
`python:slim` Dockerfiles with `apt-get update && apt-get upgrade -y`
as "the standard CIS-aligned approach" (S-06). Docker's own guidance
is rebuild-often + `--pull`/`--no-cache` (S-07). Academic work confirms
inherited-image vulns propagate and automated update mechanisms are the
gap (S-11, S-12, S-16).

## 4. Decision matrix

| Option | Fixes current 12 | Effort | Risk | Recurrence protection | Verdict |
|---|---|---|---|---|---|
| **A. `apt-get upgrade -y` in runtime stage** (both Dockerfiles) | Yes — all 12 are `fixed` | Trivial | Low-moderate (pulls all available Debian updates; small nondeterminism) | Partial — only picks up fixes at build time | **SELECT** |
| B. Wait for upstream `python:3.12-slim` rebuild | Eventually (≥monthly cadence, S-24) | Zero | Leaves 3 CRITICAL in prod meanwhile | None | Reject — leaves prod exposed |
| C. Digest-pin + Renovate/Dependabot docker updates | Indirectly (next pin bump) | Medium | Pinning freezes CVEs *until* bumped; needs bot config (S-19) | Strong (automated PRs) | Adopt later — follow-up intake |
| D. Migrate to distroless/Chainguard | Eliminates class (no pkg mgr/shell, S-09, S-22) | High | **Breaks**: `curl` healthcheck, `useradd`, apt runtime deps (libpq5), debuggability | Strong | Reject now — separate intake; revisit |
| E. `.trivyignore` suppress | No — hides them | Trivial | Violates `error-taxonomy` hard-stop intent; masks real risk | None | Reject — only for verified non-exploitable CVEs w/ expiry dates |

**Selected: Option A, plus repair of `a10-smoke.yml`, plus ruff cleanup.
Confidence: High** — corroborated by S-06 (identical fix, identical
base family), S-07 (Docker rebuild guidance), S-13 (fix versions exist).

`a10-smoke.yml` decision: **repair, don't delete** — restore `d21820c`
and add the intended "Install system dependencies" step correctly; the
job guards Alembic migrations + A10 smoke against Postgres and was
clearly intended as a gate. Prevent recurrence with `actionlint`
(S-17, S-23) — either a CI job or a documented pre-commit check.

Ruff: delete the two unused imports (auto-fixable); they are
`unused-import` class — auto-fix per `error-taxonomy` skill.

## 5. Edge-case / remediation matrix (top 30)

| # | Edge case | Impact | Remediation | Codebase check |
|---|---|---|---|---|
| 1 | `apt-get upgrade` pulls a breaking lib update (e.g. libpq ABI) | Functional | Runtime stage only installs `libpq5 curl`; run full backend test suite in CI post-change | CI backend job runs pytest after build — covered |
| 2 | Build becomes nondeterministic (different pkgs per build day) | Operational | Accept for now; Option C (digest pin + bot) is the determinism path — follow-up | No digest pinning currently |
| 3 | `apt-get upgrade` in builder stage pulls newer gcc/libpq-dev → wheel rebuild differences | Functional | Apply upgrade in **both** stages so builder/runtime libs match | Both stages apt-install; symmetric fix |
| 4 | Debian trixie point release mid-build fails `rm -rf /var/lib/apt/lists/*` ordering | Operational | Keep upgrade inside the same RUN layer as update/install | Pattern already single-layer |
| 5 | Trivy DB cache serves stale results post-fix | False-negative | `fail-on-cache-miss: false` already set; cache-dir is per-run ephemeral — safe | Verified in workflow inputs |
| 6 | New unfixed CRITICAL appears → `ignore-unfixed:true` hides it | Security | Accepted scanner semantics (S-25); periodic manual `trivy image` without flag for audit | — |
| 7 | Upgrade makes image larger → Railway deploy slower | Performance | `apt-get upgrade` adds tens of MB worst case; `--no-install-recommends` unchanged | Slim base, acceptable |
| 8 | `perl-base` removed instead of upgraded? | — | `apt-get upgrade` never removes; `dist-upgrade` would — do NOT use dist-upgrade | Use `upgrade -y` only |
| 9 | Upstream base rebuild lands same day → upgrade is no-op | None | Idempotent; harmless | — |
| 10 | gzip/pcre2/sqlite3 are transit deps we never call | Security | Still present in image → still scanned; upgrade is correct regardless of reachability (S-22 context); VEX-style suppression possible later | No `.trivyignore` exists |
| 11 | Frontend `nginx:1.29-alpine` scan later fails similarly | Security | Same treatment pattern for Alpine (`apk upgrade`) when/if it fires | Frontend scan step exists in same job |
| 12 | `backend/Dockerfile` vs root `Dockerfile` drift | Operational | Apply identical change to both; consider consolidating (separate intake) | Files differ cosmetically, same base |
| 13 | Restored a10-smoke fails because test file moved | Functional | Verify `backend/tests/test_a10_smoke.py` exists before restoring | **verify at impl time** |
| 14 | Restored a10-smoke fails on alembic env | Functional | d21820c ran migrations w/ `DATABASE_URL` postgres service — restore verbatim | Postgres service block intact in corrupt file |
| 15 | `paths:` filter skips a10-smoke on frontend-only pushes | Coverage | Intended behavior — keep filter as d21820c had it | Filter preserved in corrupt file |
| 16 | actionlint addition slows pre-commit | DX | Run as CI job (not hook) or scoped hook; single binary, <1s | No actionlint currently |
| 17 | Husky sweep-guard blocks workflow fix commit | Process | `ALLOW_WORKFLOW_CHANGES=1 git commit` — documented in AGENTS.md | Rule confirmed |
| 18 | Human's uncommitted ci.yml edit collides with fix branch | Process | Do not stage `ci.yml`; only commit a10-smoke.yml + Dockerfiles + 2 py files | Local `ci.yml` modified — flagged |
| 19 | Ruff fix in `main.py` removes symbol some dynamic import needs | Functional | `FeatureFlags` unused per ruff; `get_flags` retained; grep confirms no `FeatureFlags(` usage | Verify grep at impl |
| 20 | `pytest` import in test file needed for `pytest.fixture` later | Functional | File currently passes without it; re-add when needed | — |
| 21 | Trivy flags NEW CVEs after upgrade (next-day disclosures) | Security | Expected; gate stays green until next fixable CRITICAL — that's the gate working | — |
| 22 | `apt-get upgrade` interactive prompts | Operational | `-y` + `DEBIAN_FRONTEND=noninteractive` (slim images default noninteractive; add env if prompt appears) | Slim default fine |
| 23 | Upgrade in builder venv invalidates cached pip layer | Performance | One-time cache miss; acceptable | — |
| 24 | Railway builds different context than CI scan | Drift | CI scans root `Dockerfile`; Railway `railway up` also builds root — aligned | Verified both use root file |
| 25 | Corrupt-workflow class recurs on other files | Operational | actionlint CI job scans all `.github/workflows/*.yml` | 10 workflow files exist |
| 26 | Zero-duration failure misread as "skipped" | Observability | Repair makes failures loud again; also enables job-level failure mail | — |
| 27 | Debian archive unavailable during build (deb.debian.org blip) | Operational | `apt-get` retries; transient CI failure — rerun | Standard |
| 28 | Trivy action version drift (v0.36.0 pinned) | Supply-chain | Pinned action OK; consider SHA-pin later w/ Option C | Consistent w/ repo style |
| 29 | Fix lands on `main` but `staging` still red | Process | Merge/cherry-pick per staging promotion flow | Deploy gate per AGENTS.md |
| 30 | `security-block` skill says "do not auto-fix" — is Option A an auto-fix? | Process | Escalated HERE: this memo + ticket is the escalation; Option A needs explicit user go-ahead before implementation | `error-taxonomy` SKILL.md — **CONFLICT FLAGGED, user decision required** |

## 6. Codebase conflict check

- **`error-taxonomy` skill:** `security-block` (Trivy) → "Escalate
  immediately — do not auto-fix." The ruff F401s are `unused-import` →
  auto-fix allowed. The Trivy/Dockerfile change and the a10-smoke
  decision require user sign-off — this memo is that escalation.
- **Commit hygiene:** workflow changes need
  `ALLOW_WORKFLOW_CHANGES=1` and must be their own commit; the ruff
  fixes are a separate commit; Dockerfile(s) a third — or a single
  "ci-green" commit for non-workflow files. Never `git add -A`.
- **Uncommitted `ci.yml`** — leave untouched (human's file).
- **No journey-loop / paywall surfaces touched** — guard N/A.
- **Deploy gate:** staging only until explicit production approval.

## 7. Gaps / user input needed

1. Approve Option A (`apt-get upgrade` in root + backend Dockerfile
   runtime & builder stages) — flagged by `security-block` taxonomy.
2. `a10-smoke.yml`: confirm **repair** (restore `d21820c` + deps step)
   vs delete.
3. Approve adding `actionlint` as a CI job (prevents recurrence).
4. Defer Option C (digest pinning + Renovate) to a follow-up intake?

## 8. Related artifacts

- Intake: `.ai/intake/2026-09-15-p1-ci-red-main.md`
- Failing run: `gh run view 35023135102`
- Corrupt commit: `69d7a14`; clean ancestor: `d21820c`
