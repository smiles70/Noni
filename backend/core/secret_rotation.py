"""Non-breaking secret rotation visibility.

Secrets that support rotation metadata use the format:
    VALUE::TIMESTAMP
where TIMESTAMP is a Unix epoch integer. Secrets without this metadata
are silently accepted (no-op).

Sprint '2nd Safe Yellow' P1: adds expiry tracking without breaking
existing plain-string secrets.
"""

from __future__ import annotations

import logging
import os
import time

logger = logging.getLogger("noni.secret_rotation")

DEFAULT_MAX_AGE_SEC = 60 * 60 * 24 * 90  # 90 days


def warn_if_secret_old(name: str, max_age_sec: int = DEFAULT_MAX_AGE_SEC) -> None:
    """Log a warning if a secret with rotation metadata is older than max_age_sec.

    No-op (returns silently) if:
      - the env var is missing
      - the value does not contain '::'
      - the timestamp portion is not a valid integer
    """
    val = os.getenv(name)
    if not val:
        return

    # Only works if rotation metadata exists — otherwise no-op
    if "::" not in val:
        return

    try:
        # rsplit from the right so values that contain '::' are safe
        _, ts_str = val.rsplit("::", 1)
        age = time.time() - int(ts_str)

        if age > max_age_sec:
            logger.warning(
                "secret_rotation_due",
                extra={
                    "secret_name": name,
                    "age_days": int(age / 86400),
                    "max_days": int(max_age_sec / 86400),
                },
            )
    except Exception:
        # Never break runtime
        pass
