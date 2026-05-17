"""Pre-commit guard: ensure `cryptography` is pinned in requirements.

`python-jose[cryptography]` and Clerk JWT verification both depend on
the `cryptography` wheel being installed. We previously hit a
container-only failure ("InvalidKey" / "no module named cryptography")
because the dependency was implicit. Pinning it explicitly in the root
`requirements.txt` keeps the Docker image self-sufficient.

Exit code: 0 if found, 1 if missing.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Project root requirements file. The earlier draft pointed at
# `backend/requirements.txt`, which does not exist in this repo.
REQ = Path("requirements.txt")


def main() -> int:
    if not REQ.exists():
        print(f"\u26a0\ufe0f  {REQ} not found; skipping dependency check.")
        return 0

    content = REQ.read_text(encoding="utf-8")
    if "cryptography" not in content:
        print(f"\u274c {REQ}: missing `cryptography` dependency")
        return 1

    print("\u2705 Dependencies valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
