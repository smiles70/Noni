"""Pre-commit guard: ensure the backend still parses `Authorization: Bearer`.

A refactor that accidentally drops the Bearer-token handling silently
breaks every authenticated request. This guard asserts the literal
substrings exist somewhere in `backend/` so the wiring is not lost.

Exit code: 0 if found, 1 if missing.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path("backend")


def main() -> int:
    if not ROOT.exists():
        print("\u2705 No backend/ directory; nothing to check.")
        return 0

    for f in ROOT.rglob("*.py"):
        try:
            content = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if "Authorization" in content and "Bearer" in content:
            print("\u2705 Auth header handling exists")
            return 0

    print("\u274c No Authorization Bearer handling detected in backend/")
    return 1


if __name__ == "__main__":
    sys.exit(main())
