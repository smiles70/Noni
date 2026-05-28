# Gotchas

A running log of operational traps that have bitten this repo, with the
exact symptom, the root cause, and the verified fix. Entries are
append-only; if a gotcha recurs in a new form, add a new entry rather
than editing the old one.

The intent is not to document everything that can go wrong — only those
classes of failure that:

1. Cost more than an hour to diagnose, and
2. Will plausibly bite a future developer (or future-you) again.

---

## G2 — Login loop: `KeyError: 'levelname'` masks `TypeError` in `PyJWKClient`

**First observed:** 2026-05-27, during Module 0 curriculum implementation.
**Cost:** ~4 hours of production downtime.

### Symptom

- Frontend login loop: user signs in, backend returns `500`, frontend retries indefinitely.
- `/api/v1/auth/session` returns `500` with Bearer token, `401` without token.
- Log shows `KeyError: 'levelname'` with traceback through `starlette/middleware/errors.py`.
- After fixing the `KeyError`, login still fails with a new `TypeError` in `ClerkVerifier.__init__`.

### Root cause (two interlocking bugs)

**Bug 1 — `JsonFormatter` `rename_fields` crash:**

`backend/app/telemetry.py:252-258` configured `pythonjsonlogger.JsonFormatter` with:
```python
fmt="%(timestamp)s %(level)s %(name)s ...",
rename_fields={"levelname": "level", "asctime": "timestamp"}
```

`python-json-logger` parses `_required_fields` from the `fmt` string. Because the string used the *renamed* field names (`timestamp`, `level`) instead of the *original* names (`asctime`, `levelname`), those original keys were never populated in the formatter's internal dict. When `_perform_rename_log_fields()` executed `log_record["level"] = log_record["levelname"]`, it raised `KeyError: 'levelname'`.

This crash happened inside `Handler.emit()` → `Formatter.format()`, so `try/except` around `logger.log()` could NOT catch it. The exception propagated through Python's logging machinery, bypassed all FastAPI exception handlers, and was caught by Starlette's outermost `ServerErrorMiddleware`, which returned `PlainTextResponse("Internal Server Error", status_code=500)`.

**Bug 2 — `PyJWKClient` non-existent `cache_ttl` parameter:**

`backend/services/clerk_verifier.py:37` used:
```python
self._jwk_client = PyJWKClient(jwks_url, cache_keys=True, cache_ttl=3600)
```

PyJWT 2.10.1's `PyJWKClient` accepts `lifespan`, NOT `cache_ttl`. This raised `TypeError: PyJWKClient.__init__() got an unexpected keyword argument 'cache_ttl'`.

**Why both appeared simultaneously:**

Login was working before Module 0. Adding `curriculum_units_module_0.py` invalidated the Docker `COPY backend ./backend` layer, forcing a full rebuild. This exposed the `cache_ttl` code that had been added in a previous session but was never in a fresh image. The `JsonFormatter` bug was introduced by telemetry changes in the same deploy cycle.

The `KeyError` masked the `TypeError`: the formatter crashed BEFORE the request ever reached `ClerkVerifier.__init__()`, so the `cache_ttl` bug was invisible until the formatter was fixed.

### Confirmation procedure

```bash
# Check for KeyError in logs
/home/kim/.fly/bin/flyctl logs --app noni-api --no-tail | grep "KeyError: 'levelname'"

# Check for PyJWKClient TypeError in logs  
/home/kim/.fly/bin/flyctl logs --app noni-api --no-tail | grep "unexpected keyword argument 'cache_ttl'"

# Local reproduction:
python -c "
from pythonjsonlogger import jsonlogger
import logging
fmt = '%(timestamp)s %(level)s %(message)s'
rename = {'levelname': 'level', 'asctime': 'timestamp'}
handler = logging.StreamHandler()
handler.setFormatter(jsonlogger.JsonFormatter(fmt, rename_fields=rename))
logger = logging.getLogger('test')
logger.addHandler(handler)
logger.info('test')  # Will raise KeyError: 'levelname'
"

python -c "
from jwt import PyJWKClient
PyJWKClient('https://example.com/.well-known/jwks.json', cache_keys=True, cache_ttl=3600)
# Will raise TypeError: unexpected keyword argument 'cache_ttl'
"
```

### Fix

**For Bug 1 (JsonFormatter):**

Change `backend/app/telemetry.py:252-253` to use **original** field names in `fmt`:
```python
"%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(path)s %(status)s %(latency_ms)s"
```

`rename_fields` then safely renames `levelname` → `level` and `asctime` → `timestamp` because both original keys exist in the formatter's dict.

**For Bug 2 (PyJWKClient):**

Change `backend/services/clerk_verifier.py:37` and `:70`:
```python
self._jwk_client = PyJWKClient(jwks_url, cache_keys=True, lifespan=3600)
```

`lifespan` is the correct parameter name in PyJWT 2.10.1.

### Recommended runtime guards

1. **Never use renamed fields in `fmt` string:** The `fmt` string must reference the *original* `LogRecord` attribute names (`levelname`, `asctime`). `rename_fields` operates AFTER the dict is populated.

2. **Verify PyJWKClient parameters against installed version:** Before adding JWKS configuration, run:
   ```bash
   python -c "import inspect; from jwt import PyJWKClient; print(inspect.signature(PyJWKClient.__init__))"
   ```

3. **Test auth path after ANY backend change:** Even "unrelated" changes (curriculum, telemetry) can invalidate Docker cache and expose latent bugs.

### Cross-references

- `backend/app/telemetry.py:250-265` (`_setup_json_logging`)
- `backend/services/clerk_verifier.py:32-72` (`ClerkVerifier.__init__` and retry block)
- [python-json-logger source code](https://github.com/madzak/python-json-logger/blob/master/src/pythonjsonlogger/jsonlogger.py) — `_perform_rename_log_fields` direct dict access
- [PyJWT PyJWKClient docs](https://pyjwt.readthedocs.io/en/latest/usage.html) — `lifespan` parameter

---

## G1 — Missing `cryptography` extra silently breaks Clerk auth (RS256)

**First observed:** earlier in Sprint 22 (recorded informally).
**Second observed:** 2026-05-17, during Stage 2 login redesign runtime
validation. Cost ~30 hours of diagnosis the second time.

### Symptom

- `GET /auth/session` returns `401` with
  `{"detail":{"error":{"code":"auth.transient_verifier_unavailable",
  "message":"Identity provider verification is temporarily unavailable."}}}`.
- Backend log shows the request completing in ~3 ms — far too fast for
  a real JWKS network fetch. (After the fix, the same request takes
  ~12 ms because the verifier actually runs.)
- The frontend `AuthProvider` enters `TRANSIENT_ERROR` and never reaches
  `READY`. To the user this appears as a "stuck on signing in" or
  "login loop" depending on how the UI surfaces the state.
- Every other diagnostic comes back clean:
  - `CLERK_JWKS_URL` is set and resolves.
  - JWKS endpoint reachable; returns 1 key with the expected `kid`.
  - Frontend `VITE_CLERK_PUBLISHABLE_KEY` instance subdomain matches
    backend `CLERK_JWKS_URL` (i.e. NOT an instance mismatch).
  - Backend `/auth/config` returns the expected `provider=clerk`.
- A no-auth call to `/auth/session` correctly returns
  `auth.no_credential` — proving the route, telemetry, and envelope
  shape are fine. **The failure is entirely inside the verifier.**

### Why it hides

`PyJWT[crypto]==2.10.1` declares `cryptography` as an extra. If the
venv has PyJWT installed but `cryptography` is missing (e.g. because
someone ran `pip install pyjwt` instead of `pip install -r requirements.txt`,
or because a `pip uninstall cryptography` slipped into a previous
session), then `PyJWKClient.get_signing_key_from_jwt()` or
`jwt.decode(..., algorithms=["RS256"])` raises an exception that
`_verify_clerk()` catches as a generic `Exception` and remaps to
`auth.transient_verifier_unavailable` — the same code emitted for a
genuine JWKS network outage. The discriminated-error system, which
exists precisely to tell ops faults from user faults, *correctly*
classifies this as "ops fault", but the log line that names the
underlying exception class is the only signal of which ops fault, and
that line lands on a logger whose handler may not be attached under
uvicorn's default log config.

The combination — same error code as a transient outage, log line
suppressed, latency too small to look like a network call — produces
a diagnosis dead end.

### Confirmation procedure

From inside the venv:

```bash
python -c "import cryptography; print(cryptography.__version__)"
# MUST print 43.0.3 (the requirements.txt pin). ImportError = G1.
```

If that import fails while `import jwt` works, you have G1.

### Fix

```bash
source /mnt/c/Users/kimem/Noni/venv/bin/activate
pip install -r requirements.txt
# verify:
python -c "import cryptography; assert cryptography.__version__ == '43.0.3'; print('OK')"
# restart uvicorn so the new module is loaded:
lsof -i :8000 -t | xargs -r kill -9
uvicorn backend.app.main:app --port 8000
```

### Recommended runtime guard

Add a startup probe in `backend/app/main.py` (deferred until ADR 0026
lands) that does:

```python
if settings.AUTH_PROVIDER == "clerk":
    try:
        from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey  # noqa: F401
    except ImportError as e:
        raise RuntimeError(
            "AUTH_PROVIDER=clerk requires the `cryptography` package "
            "(PyJWT[crypto] extra). Run `pip install -r requirements.txt`. "
            f"Underlying ImportError: {e}"
        )
```

This fails the process at startup instead of letting it serve broken
401s indefinitely. Open a follow-up ADR before adding.

### Cross-references

- `requirements.txt` line 12 (`cryptography==43.0.3`)
- `backend/services/auth_verifier.py:180-194` (the catch-all that
  converts the missing-extra `Exception` into
  `auth.transient_verifier_unavailable`)
- ADR 0012 (pinned dependencies) — the policy this gotcha violates
  when a venv goes out of sync with `requirements.txt`.

---

## G3 — Frontend deployed with `localhost` API base URL

**First observed:** 2026-05-28, during help center deployment.
**Cost:** Production site down, user-facing "This page is paused" error, reputational damage.

### Symptom

- Deployed frontend shows "This page is paused." immediately after loading.
- Browser devtools Network tab shows failed requests to `http://localhost:8000/api/...`
- The backend (`noni-api.fly.dev`) is healthy and responding normally.
- The failure is invisible until a user loads the deployed site; local dev works fine.

### Root cause

`frontend/src/lib/env.ts` defines:
```typescript
export const API_BASE_URL: string = (
  _env.VITE_API_BASE_URL ?? "http://localhost:8000"
).replace(/\/+$/, "");
```

Vite inlines environment variables at **build time**. If `VITE_API_BASE_URL` is not present in the shell environment during `vite build`, the default `http://localhost:8000` is baked into the bundle. Every deployed user then tries to call their own localhost, which fails.

The build command was:
```bash
./node_modules/.bin/tsc -b && ./node_modules/.bin/vite build
```

The `VITE_API_BASE_URL=https://noni-api.fly.dev` prefix was missing.

### Confirmation procedure

```bash
# After build, before deploy, grep the bundle for localhost:
grep -r "localhost:8000" dist/
# Any match = G3. The bundle must be rebuilt.

# Or check the deployed site:
curl -s https://<deployed-frontend-url>/ | grep -o 'localhost:8000' | head -1
```

### Fix

Rebuild with the environment variable set via `.env.production` (most reliable for WSL):
```bash
cd frontend
printf "VITE_API_BASE_URL=https://noni-api.fly.dev\n" > .env.production
./node_modules/.bin/tsc -b && ./node_modules/.bin/vite build
```

Then redeploy the `dist/` directory.

### Recommended runtime guards

1. **Never run `vite build` without `VITE_API_BASE_URL` in production builds.** Add a pre-build check to `frontend/package.json` scripts:
   ```json
   "build:prod": "test -n \"$VITE_API_BASE_URL\" && tsc -b && vite build"
   ```

2. **Verify bundle after build, before deploy.** Add a CI step:
   ```bash
   if grep -r "localhost:8000" dist/; then echo "FAIL: localhost in bundle"; exit 1; fi
   ```

3. **Prefer `.env.production` over shell env vars for WSL builds.** WSL command quoting is unreliable for env var propagation through `wsl.exe bash -lc`.

### Cross-references

- `frontend/src/lib/env.ts:13-15` (`API_BASE_URL` default)
- `docs/staging-deploy.md:66` (`VITE_API_BASE_URL` mentioned as required)
- `frontend/package.json:8` (build scripts)

---
