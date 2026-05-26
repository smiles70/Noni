"""Celery app configuration.

Sprint 27 H4: background job queue for webhooks, telemetry exports, and
account cleanup. Redis is the broker; Fly Redis or Upstash Redis.
"""

from celery import Celery

from backend.core.config import settings

# Redis broker URL from env (Fly Redis sets REDIS_URL automatically).
broker_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")

app = Celery(
    "noni",
    broker=broker_url,
    backend=broker_url,
    include=["backend.tasks.webhook_tasks"],
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
)
