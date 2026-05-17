"""Pre-commit guard: envelope changes must be paired with envelope tests.

`backend/models/ui_state_envelope.py` defines the authorized UI contract
(components, actions, transitions). Silently mutating it without updating
`backend/tests/test_ui_state_envelope.py` has caused contract drift before.

This guard enforces a coupled-edit invariant: if the envelope file is
staged for commit, the matching test file must also be staged.

Opt-out: set `NONI_SKIP_ENVELOPE_PIN=1` in the environment for deliberate
test-free changes (e.g. comment-only edits).
"""

from __future__ import annotations

import os
import subprocess
import sys

ENVELOPE_FILE = "backend/models/ui_state_envelope.py"
TEST_FILE = "backend/tests/test_ui_state_envelope.py"
OPT_OUT_ENV = "NONI_SKIP_ENVELOPE_PIN"


def staged_files() -> set[str]:
    """Return the set of paths staged in the current commit."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return set()
    return {
        line.strip().replace("\\", "/")
        for line in result.stdout.splitlines()
        if line.strip()
    }


def main() -> int:
    if os.environ.get(OPT_OUT_ENV):
        print(f"\u23ed  Envelope pin guard skipped via {OPT_OUT_ENV}.")
        return 0

    staged = staged_files()
    if ENVELOPE_FILE not in staged:
        print("\u2705 Envelope file not staged; nothing to check.")
        return 0

    if TEST_FILE not in staged:
        print(
            f"\u274c {ENVELOPE_FILE} is staged but {TEST_FILE} is not.\n"
            "Envelope mutations must be paired with test updates to "
            "prevent silent UI-contract drift.\n"
            f"Either update {TEST_FILE} in this commit, or set "
            f"{OPT_OUT_ENV}=1 for deliberate test-free edits."
        )
        return 1

    print("\u2705 Envelope and tests staged together.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
