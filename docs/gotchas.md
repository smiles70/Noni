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
