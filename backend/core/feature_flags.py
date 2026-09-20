"""Environment-variable-backed feature flags.

Flags are read once at startup from `FEATURE_<NAME>` environment variables.
Values are considered enabled when they are one of: `1`, `true`, `yes`, `on`
(case-insensitive). Any other value, or a missing variable, means disabled.
"""

import os
from typing import Dict, List

TRUTHY: List[str] = ["1", "true", "yes", "on"]


class FeatureFlags:
    """Runtime feature-flag container."""

    def __init__(self, env: Dict[str, str] | None = None) -> None:
        env = env or os.environ
        self._flags: Dict[str, bool] = {}
        for key, value in env.items():
            if key.startswith("FEATURE_"):
                flag_name = key.removeprefix("FEATURE_").lower()
                self._flags[flag_name] = value.lower() in TRUTHY

    def is_enabled(self, name: str) -> bool:
        """Return True if the named feature is enabled."""
        return self._flags.get(name.lower(), False)

    def all_enabled(self) -> List[str]:
        """Return the list of enabled flag names."""
        return [name for name, enabled in self._flags.items() if enabled]


def get_flags() -> FeatureFlags:
    """Factory that returns the process-wide feature flags."""
    return FeatureFlags()
