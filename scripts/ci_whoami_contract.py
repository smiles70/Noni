"""CI contract: GET /auth/whoami with a malformed Bearer token must NOT 500.

A 500 on whoami caused the frontend's auth bootstrap to retry forever,
producing the infinite redirect loop observed during the auth sprint.
The correct behavior is a clean 401 (or 403). Anything in the 5xx range
is a regression.

Pair with `ci_auth_test.py`. Together they pin the two failure modes of
the auth gate: silent success (anonymous getting through) and ungraceful
failure (malformed credential crashing the route).
"""

from __future__ import annotations

import sys

import requests

URL = "http://127.0.0.1:8000/auth/whoami"
HEADERS = {"Authorization": "Bearer invalid.token.value"}
TIMEOUT_SECONDS = 10


def main() -> int:
    try:
        r = requests.get(URL, headers=HEADERS, timeout=TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        print(f"\u274c whoami unreachable: {exc}")
        return 1

    if 500 <= r.status_code < 600:
        print(
            f"\u274c whoami returned HTTP {r.status_code} on a malformed "
            f"Bearer token; must be 4xx. Body: {r.text[:200]!r}"
        )
        return 1

    print(
        f"\u2705 whoami stability OK "
        f"(HTTP {r.status_code} on malformed token, not 5xx)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
