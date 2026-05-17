"""Pre-commit guard: prevent SQLAlchemy `.one()` crashes.

`.one()` raises `NoResultFound` / `MultipleResultsFound`, which surface
to the user as a generic 500. The safe form is `.one_or_none()` followed
by an explicit None check, or `.first()` for cases where None is fine.

Scope:
  - Production code under `backend/` except `backend/tests/`.
  - Lines carrying the marker `# db-one-allowed` are skipped
    (use this for rare cases where `.one()` is deliberately invariant-
    protecting, e.g. re-fetch after IntegrityError where existence is
    guaranteed by the DB constraint that just fired).

Exit code: 0 if clean, 1 if any unmarked `.one()` found in production.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PATTERN = re.compile(r"\.one\(\)")
ALLOW_MARKER = "# db-one-allowed"
ROOT = Path("backend")
EXCLUDE_DIRS = {"tests"}


def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDE_DIRS for part in path.parts)


def main() -> int:
    errors: list[str] = []
    if not ROOT.exists():
        print("\u2705 No backend/ directory; nothing to check.")
        return 0

    for f in ROOT.rglob("*.py"):
        if is_excluded(f):
            continue
        try:
            lines = f.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(lines, start=1):
            if PATTERN.search(line) and ALLOW_MARKER not in line:
                errors.append(
                    f"{f}:{lineno}: uses .one() \u2014 use .one_or_none() "
                    f"or annotate with `{ALLOW_MARKER}` if intentional."
                )

    if errors:
        print("\n\u274c Unsafe DB query usage:\n")
        print("\n".join(errors))
        return 1

    print("\u2705 DB query patterns safe")
    return 0


if __name__ == "__main__":
    sys.exit(main())
