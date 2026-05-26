"""CurriculumLoader — unified content loader for all modules.

Sprint 28-C.6: replaces scattered per-module curriculum_units*.py imports
with a single loader that reads from the content/ directory.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_CONTENT_DIR = Path(__file__).parent / "curriculum"


class CurriculumLoader:
    """Load curriculum pages and units from JSON files.

    Falls back to the legacy in-module Python structures when a file is
    absent, so the migration can be incremental (one unit at a time).
    """

    @staticmethod
    def _load_json(filename: str) -> dict[str, Any] | None:
        path = _CONTENT_DIR / filename
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    @classmethod
    def get_unit(cls, module: int, unit_id: str) -> dict[str, Any] | None:
        """Return the full unit dict for a given module + unit_id."""
        data = cls._load_json(f"module_{module}.json")
        if data is None:
            return None
        for unit in data.get("units", []):
            if unit.get("unit_id") == unit_id:
                return unit
        return None

    @classmethod
    def list_units(cls, module: int) -> list[dict[str, Any]]:
        """Return all units for a module."""
        data = cls._load_json(f"module_{module}.json")
        if data is None:
            return []
        return data.get("units", [])

    @classmethod
    def get_standalone_pages(cls, page_id: str) -> list[dict[str, Any]] | None:
        """Return hard-coded standalone pages (e.g. what-is-ai)."""
        data = cls._load_json("standalone.json")
        if data is None:
            return None
        return data.get(page_id)
