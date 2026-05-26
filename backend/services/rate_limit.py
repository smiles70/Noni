"""Application-level rate limiting with Redis token bucket + DB fallback.

See ADR 0024. Production uses Redis token buckets when REDIS_URL is set.
Local/test environments fall back to Postgres fixed-window counters: one
row per (action, identifier, window_start). The pg_cron sweep job removes
rows past `expires_at`.

This is defense in depth — Cloudflare WAF is the primary limiter. The
DB-backed layer exists for per-account or per-resource limits that the
WAF cannot express.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DbSession

from backend.core.config import settings
from backend.models.governance import RateLimitCounter

log = logging.getLogger(__name__)

_REDIS_RATE_LIMIT_SCRIPT = """
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now_ms = tonumber(ARGV[3])
local ttl_ms = tonumber(ARGV[4])

local bucket = redis.call('HMGET', key, 'tokens', 'ts')
local tokens = tonumber(bucket[1])
local ts = tonumber(bucket[2])

if tokens == nil then
  tokens = capacity
  ts = now_ms
end

local elapsed = math.max(0, now_ms - ts) / 1000
tokens = math.min(capacity, tokens + (elapsed * refill_rate))

if tokens < 1 then
  redis.call('HMSET', key, 'tokens', tokens, 'ts', now_ms)
  redis.call('PEXPIRE', key, ttl_ms)
  return 0
end

tokens = tokens - 1
redis.call('HMSET', key, 'tokens', tokens, 'ts', now_ms)
redis.call('PEXPIRE', key, ttl_ms)
return 1
"""

_redis_client = None


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class RateLimit:
    action: str
    max_per_window: int
    window_seconds: int

    def key(
        self, identifier: str, *, now: datetime | None = None
    ) -> tuple[str, datetime]:
        now = now or _utcnow()
        bucket = int(now.timestamp() // self.window_seconds) * self.window_seconds
        window_start = datetime.fromtimestamp(bucket, tz=timezone.utc)
        # Hash the identifier to bound key length and avoid PII in the table.
        ident_hash = hashlib.sha256(identifier.encode("utf-8")).hexdigest()[:32]
        return f"{self.action}:{ident_hash}:{bucket}", window_start

    def redis_key(self, identifier: str) -> str:
        ident_hash = hashlib.sha256(identifier.encode("utf-8")).hexdigest()[:32]
        return f"ratelimit:token_bucket:{self.action}:{ident_hash}"


def _get_redis_client():
    global _redis_client
    if not settings.REDIS_URL:
        return None
    if _redis_client is not None:
        return _redis_client
    try:
        import redis

        _redis_client = redis.Redis.from_url(
            settings.REDIS_URL,
            socket_connect_timeout=1.0,
            socket_timeout=1.0,
            decode_responses=True,
        )
        _redis_client.ping()
        return _redis_client
    except Exception as exc:
        log.warning("redis_rate_limit_unavailable", extra={"error": str(exc)})
        _redis_client = None
        return None


def _check_redis_token_bucket(limit: RateLimit, identifier: str) -> bool | None:
    client = _get_redis_client()
    if client is None:
        return None
    now_ms = int(_utcnow().timestamp() * 1000)
    refill_rate = limit.max_per_window / limit.window_seconds
    ttl_ms = max(limit.window_seconds * 2 * 1000, 1000)
    try:
        allowed = client.eval(
            _REDIS_RATE_LIMIT_SCRIPT,
            1,
            limit.redis_key(identifier),
            limit.max_per_window,
            refill_rate,
            now_ms,
            ttl_ms,
        )
        return int(allowed) == 1
    except Exception as exc:
        log.warning("redis_rate_limit_failed", extra={"error": str(exc)})
        return None


def check_and_increment(db: DbSession, limit: RateLimit, identifier: str) -> bool:
    """Return True if the request is permitted, False if over the limit.

    Caller MUST commit if returned True and the request should be
    counted. If False, no commit is necessary; the row exists already.
    """
    redis_result = _check_redis_token_bucket(limit, identifier)
    if redis_result is not None:
        return redis_result

    key, window_start = limit.key(identifier)
    expires_at = window_start + timedelta(seconds=limit.window_seconds)

    row = (
        db.query(RateLimitCounter)
        .filter(RateLimitCounter.key == key)
        .with_for_update(skip_locked=False)
        .one_or_none()
    )
    if row is None:
        try:
            db.add(
                RateLimitCounter(
                    key=key,
                    count=1,
                    window_start=window_start,
                    expires_at=expires_at,
                )
            )
            db.flush()
            return True
        except IntegrityError:
            db.rollback()
            # Re-fetch after the unique-constraint violation we just caught:
            # the row MUST exist now (another tx created it). .one_or_none()
            # would silently mask a real invariant break.
            q = db.query(RateLimitCounter).filter(RateLimitCounter.key == key)
            row = q.one()  # db-one-allowed

    if row.count >= limit.max_per_window:
        return False
    row.count += 1
    db.flush()
    return True


def enforce(
    db: DbSession,
    limit: RateLimit,
    identifier: str,
    envelope_id: str = "ratelimit.exceeded",
) -> None:
    """Convenience: raise 429 with an envelope id if over the limit."""
    if not check_and_increment(db, limit, identifier):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"envelope_id": envelope_id},
        )


def client_ip(request: Request) -> str:
    """Return a best-effort client IP. Honors Cloudflare's CF-Connecting-IP."""
    return (
        request.headers.get("cf-connecting-ip")
        or request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or (request.client.host if request.client else "0.0.0.0")
    )


# Common limits used across routes.
LIMIT_AUTH_CALLBACK_PER_IP = RateLimit(
    action="auth_callback", max_per_window=20, window_seconds=60
)
LIMIT_DELETION_PER_ACCOUNT = RateLimit(
    action="account_delete", max_per_window=5, window_seconds=3600
)
LIMIT_GIFT_CLAIM_PER_IP = RateLimit(
    action="gift_claim", max_per_window=10, window_seconds=600
)
