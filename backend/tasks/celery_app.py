"""Celery app configuration.

Sprint 27 H4: background job queue for webhooks, telemetry exports, and
account cleanup. Redis is the broker; Fly Redis or Upstash Redis.
"""

import importlib
import pkgutil

from celery import Celery

from backend.core.config import settings

# Worker context: register every ORM model so string relationships
# (e.g. Purchase -> "Account") resolve inside tasks. Web workers get
# this transitively via the route graph; the Celery worker does not.
import backend.models

for _m in pkgutil.iter_modules(backend.models.__path__):
    importlib.import_module(f"backend.models.{_m.name}")

# Redis broker URL from env (Fly Redis sets REDIS_URL automatically).
broker_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")

app = Celery(
    "noni",
    broker=broker_url,
    backend=broker_url,
    include=["backend.tasks.webhook_tasks", "backend.tasks.telemetry_tasks"],
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    worker_prefetch_multiplier=1,  # fair scheduling for long tasks
    # E71-B1: named-queue routing. Without this every task lands on the
    # default "celery" queue that specialized workers don't consume.
    task_routes={
        "backend.tasks.webhook_tasks.process_stripe_webhook": {"queue": "realtime"},
        "backend.tasks.telemetry_tasks.*": {"queue": "events"},
        "backend.tasks.webhook_tasks.export_telemetry_csv": {"queue": "batch"},
        "backend.tasks.webhook_tasks.cleanup_deleted_accounts": {"queue": "batch"},
    },
)
