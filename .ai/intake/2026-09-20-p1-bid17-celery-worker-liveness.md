# PS-BID17-007 — Celery/Redis worker liveness had no HTTP probe

**Status:** RESOLVED 2026-09-20 via Railway CLI | **Severity:** P1 verification gap
**Source:** staging integration check 2026-09-20

## Problem statement

The inquiry receipt (`delivered:true`) proved the FastAPI side queued
background work. Worker-side liveness (Celery consuming from Redis)
had no HTTP surface — a dead worker would silently accept receipts
while tasks never ran.

## Resolution — Railway CLI direct check

- `noni-worker` service: **Online** (deployment `1204faa3`)
- `Redis` service (redis:8.2): **Online**
- Worker logs: `celery@b377b2452428 ready` @ 12:34:37 UTC,
  `Connected to redis://…:6379/0`, `mingle: sync complete`,
  queues bound (`ai` exchange), task modules registered
  (`telemetry_tasks`, `webhook_tasks`, `process_stripe_webhook`),
  beat scheduler running, concurrency 48 prefork.
- Cosmetic only: `CPendingDeprecationWarning` for Celery 6.0;
  `missed heartbeat` from a superseded worker node (new worker active).

## Acceptance — met

Worker verified running + consuming on staging Railway project.
No code change required.
