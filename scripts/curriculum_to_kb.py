"""Generate Retell knowledge-base docs from the curriculum models.

PS-020: the voice receptionist's KB held only site/topic docs — no
curriculum content — so she could not help a caller stuck on a unit.

This script is the single source of truth for that corpus: it imports
the unit models directly (never hand-copied text) and emits one
markdown file per module under retell/kb/curriculum/. Output is
deterministic and committed — a curriculum edit shows up as a
reviewable diff in these files, and `--check` lets CI catch drift.

Usage:
    .venv/bin/python scripts/curriculum_to_kb.py            # write docs
    .venv/bin/python scripts/curriculum_to_kb.py --check    # drift check
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.models.curriculum import CurriculumPage  # noqa: E402
from backend.models.curriculum_units import (  # noqa: E402
    BRIDGE_UNITS,
    UNITS,
    CurriculumUnit,
)
from backend.models.curriculum_units_module_0 import UNITS_MODULE_0  # noqa: E402
from backend.models.curriculum_units_module_2 import UNITS_MODULE_2  # noqa: E402
from backend.models.curriculum_units_module_3 import UNITS_MODULE_3  # noqa: E402
from backend.models.curriculum_units_module_4 import UNITS_MODULE_4  # noqa: E402
from backend.models.curriculum_units_module_5 import UNITS_MODULE_5  # noqa: E402

OUT_DIR = ROOT / "retell" / "kb" / "curriculum"

# (filename, title, units) — module 1 lives in curriculum_units.py's
# UNITS; BRIDGE_UNITS are the two connector lessons appended to it.
MODULES = [
    ("module-0", "Module 0 — What people mean when they say AI", UNITS_MODULE_0),
    ("module-1", "Module 1 — Meet Claude", UNITS + BRIDGE_UNITS),
    ("module-2", "Module 2", UNITS_MODULE_2),
    ("module-3", "Module 3", UNITS_MODULE_3),
    ("module-4", "Module 4", UNITS_MODULE_4),
    ("module-5", "Module 5", UNITS_MODULE_5),
]

GUIDANCE = (
    "This file is curriculum reference for the voice receptionist. "
    "Use it to help a caller who is stuck on a lesson: explain the idea "
    "in plain words, then point them back to the unit. For practice "
    "questions, coach the caller toward the answer — never read the "
    "marked correct answer aloud. Keep answers short."
)


def _render_page(page: CurriculumPage) -> list[str]:
    lines = [f"#### {page.title}", ""]
    lines += [f"{p}\n" for p in page.content]
    if page.principle:
        lines += [f"**Key idea:** {page.principle}", ""]
    if page.example:
        ex = page.example
        lines += [
            f"*Example — {ex.situation}*",
            "",
            f"Claude might say: “{ex.claude_says}”",
            "",
            f"Takeaway: {ex.takeaway}",
            "",
        ]
    if page.retrieval:
        r = page.retrieval
        lines += [f"*Practice question:* {r.prompt}", ""]
        for c in r.choices:
            lines.append(f"- {c.text}")
        correct = next(c for c in r.choices if c.id == r.correct_id)
        lines += [
            "",
            f"> Correct answer (do not read verbatim — guide the caller): "
            f"{correct.text}. Why: {r.explanation}",
            "",
        ]
    return lines


def _render_module(title: str, units: list[CurriculumUnit]) -> str:
    out = [f"# {title}", "", GUIDANCE, ""]
    for u in units:
        out += [f"## {u.title}", "", u.description, ""]
        for p in u.pages:
            out += _render_page(p)
    return "\n".join(out).rstrip() + "\n"


def expected_outputs() -> dict[str, str]:
    return {
        f"{name}.md": _render_module(title, units)
        for name, title, units in MODULES
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="verify committed docs match generated output")
    args = ap.parse_args()

    outputs = expected_outputs()
    if args.check:
        stale = [
            name
            for name, text in outputs.items()
            if not (OUT_DIR / name).exists() or (OUT_DIR / name).read_text() != text
        ]
        if stale:
            print(f"STALE: {stale} — run scripts/curriculum_to_kb.py")
            return 1
        print(f"fresh: {len(outputs)} curriculum docs match the models")
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, text in outputs.items():
        (OUT_DIR / name).write_text(text)
        print(f"wrote {OUT_DIR / name} ({len(text)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
