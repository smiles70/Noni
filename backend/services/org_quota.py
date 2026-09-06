"""Per-organization admission quota (E71-B3).

Tenant fairness for the B2B2C model: an account belongs to an org via a
redeemed AccessCode -> OrgLicense -> Organization. When one institution
onboards thousands of learners at once (the 9:00 AM midterm), their
request rate is capped per-org so smaller cohorts keep working.

Design notes:
- Reuses the Redis token bucket from rate_limit.py (no new infra).
- Org mapping is cached in Redis for 5 minutes — resolution costs one
  indexed join on a miss, zero DB hits on a hit.
- Over-quota returns 429 + Retry-After (calm, retryable) — never 500.
- Fails OPEN: if Redis is down or the account has no org, the request
  proceeds. This is protection, not a hard gate.
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from typing import Optional

from sqlalchemy.orm import Session as DbSession

from backend.core.config import settings
from backend.models.organizations import AccessCode, OrgLicense
from backend.services.rate_limit import RateLimit, _check_redis_token_bucket, _get_redis_client

log = logging.getLogger(__name__)

_ORG_CACHE_TTL_SECONDS = 300

# Per-org admission budget: requests per rolling minute. Sized so a
# 10k-learner institution gets ~600/min (10/min/learner burst headroom)
# while smaller cohorts always have dedicated worker capacity.
_ORG_QUOTA = RateLimit(
    action="org_admission",
    max_per_window=getattr(settings, "ORG_REQUESTS_PER_MINUTE", 600),
    window_seconds=60,
)


def _org_cache_key(account_id: uuid.UUID) -> str:
    return f"org_of:{account_id}"


def resolve_org_id(db: DbSession, account_id: uuid.UUID) -> Optional[str]:
    """Org id for the account's claimed access code, or None. Cached."""
    client = _get_redis_client()
    cache_key = _org_cache_key(account_id)
    if client is not None:
        try:
            cached = client.get(cache_key)
            if cached is not None:
                return cached or None
        except Exception:
            pass

    row = (
        db.query(OrgLicense.organization_id)
        .join(AccessCode, AccessCode.license_id == OrgLicense.id)
        .filter(AccessCode.claimed_by_account_id == account_id)
        .first()
    )
    org_id = str(row[0]) if row else None

    if client is not None:
        try:
            # Empty string = known "no org" so negatives cache too.
            client.setex(cache_key, _ORG_CACHE_TTL_SECONDS, org_id or "")
        except Exception:
            pass
    return org_id


def org_admission_allowed(org_id: str) -> bool:
    """True = proceed. False = over quota. Fails open without Redis."""
    result = _check_redis_token_bucket(_ORG_QUOTA, hashlib.sha256(org_id.encode()).hexdigest()[:16])
    return result is not False
