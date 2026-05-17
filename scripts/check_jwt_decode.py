"""Pre-commit guard: ensure every `jwt.decode(` call disables `aud`.

Clerk-issued JWTs do not always include a stable `aud` claim that
matches our backend identifier. A `jwt.decode(...)` without
`options={"verify_aud": False}` (or `audience=...`) raises
`InvalidAudienceError` at runtime, which we historically misdiagnosed
as a "broken Clerk integration."

Scope:
  - Production code under `backend/`.
  - Per-file check: if a file contains `jwt.decode(`, the same file
    must also reference `verify_aud` somewhere (typical pattern:
    `options={"verify_aud": False}` near the decode call).

Exit code: 0 if clean, 1 if any `jwt.decode(` site lacks the marker.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path("backend")


def main() -> int:
    errors: list[str] = []
    if not ROOT.exists():
        print("\u2705 No backend/ directory; nothing to check.")
        return 0

    for f in ROOT.rglob("*.py"):
        try:
            content = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if "jwt.decode(" in content and "verify_aud" not in content:
            errors.append(f"{f}: jwt.decode() without verify_aud configuration")

    if errors:
        print("\n\u274c JWT decode misconfigured:\n")
        print("\n".join(errors))
        return 1

    print("\u2705 JWT config safe")
    return 0


if __name__ == "__main__":
    sys.exit(main())
