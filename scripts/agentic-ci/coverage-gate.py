#!/usr/bin/env python3
"""Assert backend statement and branch coverage as two separate gates.

Why this exists: `coverage.py`'s `fail_under` collapses to a single number.
Once `branch = true` is enabled that number becomes a *combined*
statement+branch score, which is lower than statement coverage and is not a
threshold anyone targets. Gating on it would fail CI on a codebase whose
statement coverage is comfortably above target.

This reads the `coverage.json` produced by
`pytest --cov-branch --cov-report=json:coverage.json` and checks the two
metrics independently.

Usage:
    python scripts/agentic-ci/coverage-gate.py
    python scripts/agentic-ci/coverage-gate.py --warn
    python scripts/agentic-ci/coverage-gate.py --statement 87 --branch 75

Exit codes:
    0  both thresholds met (or --warn given)
    1  a threshold was missed
    2  coverage.json missing or unreadable
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

DEFAULT_STATEMENT = 87.0
DEFAULT_BRANCH = 75.0
DEFAULT_REPORT = "coverage.json"


def _pct(covered: int, total: int) -> float:
    """Percentage, treating a zero denominator as fully covered."""
    return 100.0 if total == 0 else 100.0 * covered / total


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    parser.add_argument("--statement", type=float, default=DEFAULT_STATEMENT)
    parser.add_argument("--branch", type=float, default=DEFAULT_BRANCH)
    parser.add_argument(
        "--warn",
        action="store_true",
        help="report shortfalls but always exit 0 (rollout mode)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="show N modules with the most missing branches when short",
    )
    args = parser.parse_args()

    report = Path(args.report)
    if not report.is_file():
        print(f"coverage-gate: {report} not found.", file=sys.stderr)
        print(
            "Run pytest first; pytest.ini writes it via "
            "--cov-report=json:coverage.json",
            file=sys.stderr,
        )
        return 2

    try:
        data = json.loads(report.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"coverage-gate: cannot read {report}: {exc}", file=sys.stderr)
        return 2

    totals = data["totals"]
    stmt_total = totals["num_statements"]
    stmt_covered = totals["covered_lines"]
    branch_total = totals["num_branches"]
    branch_covered = totals["covered_branches"]

    stmt_pct = _pct(stmt_covered, stmt_total)
    branch_pct = _pct(branch_covered, branch_total)

    stmt_ok = stmt_pct >= args.statement
    branch_ok = branch_pct >= args.branch

    def line(
        label: str, pct: float, target: float, cov: int, tot: int, ok: bool
    ) -> str:
        mark = "PASS" if ok else "FAIL"
        gap = "" if ok else f"  (short {target - pct:.2f} pt)"
        return f"  [{mark}] {label:<10} {pct:6.2f}%  target {target:.2f}%  {cov}/{tot}{gap}"

    print("coverage-gate: backend thresholds")
    print(
        line("statement", stmt_pct, args.statement, stmt_covered, stmt_total, stmt_ok)
    )
    print(
        line("branch", branch_pct, args.branch, branch_covered, branch_total, branch_ok)
    )

    if not branch_ok:
        needed = math.ceil(args.branch / 100.0 * branch_total) - branch_covered
        print(f"\n  need +{needed} covered branches to reach {args.branch:.0f}%")
        worst = sorted(
            (
                (f["summary"]["missing_branches"], name)
                for name, f in data["files"].items()
                if f["summary"]["missing_branches"]
            ),
            reverse=True,
        )[: args.top]
        if worst:
            print("  highest-yield modules (missing branches):")
            for missing, name in worst:
                print(f"    {missing:>4}  {name}")

    if not stmt_ok:
        needed = math.ceil(args.statement / 100.0 * stmt_total) - stmt_covered
        print(f"\n  need +{needed} covered statements to reach {args.statement:.0f}%")

    if stmt_ok and branch_ok:
        return 0
    if args.warn:
        print("\ncoverage-gate: below target, but --warn given; not failing.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
