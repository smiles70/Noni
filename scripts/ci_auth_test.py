"""CI contract: GET /api/v1/auth/session without a Bearer token must NOT return 200.

We accept 401 (unauthorized). Anything else — 200, 500, or a redirect —
means the auth gate has been weakened.

This is one of the two scripts that protect against the "infinite auth
loop" regression we paid for once. Pair with `ci_whoami_contract.py`.
"""

from __future__ import annotations

import sys

import requests

URL = "http://127.0.0.1:8000/api/v1/auth/session"
TIMEOUT_SECONDS = 10


def main() -> int:
    try:
        r = requests.get(URL, timeout=TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        print(f"\u274c auth session unreachable: {exc}")
        return 1

    if r.status_code != 401:
        print(
            f"\u274c auth session should reject anonymous callers; "
            f"got HTTP {r.status_code}. Body: {r.text[:200]!r}"
        )
        return 1

    print(f"\u2705 Auth baseline OK (HTTP {r.status_code} for anonymous GET)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
