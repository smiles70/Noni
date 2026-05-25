# syntax=docker/dockerfile:1.6
# Multi-stage build for the Noni backend (FastAPI + SQLAlchemy + Alembic).

# ---------- Stage 1: builder ----------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Build deps for psycopg2 + cryptography wheels.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cache dependency layer.
COPY requirements.txt ./
RUN pip install --prefix=/install -r requirements.txt

# ---------- Stage 2: runtime ----------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Runtime libs only (libpq for psycopg2). Add curl for HEALTHCHECK.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 noni

WORKDIR /app

# Bring in installed deps from builder.
COPY --from=builder /install /usr/local

# Project source. .dockerignore keeps frontend, tests, node_modules out.
COPY alembic.ini ./
COPY alembic ./alembic
COPY backend ./backend
COPY scripts ./scripts

USER noni

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://127.0.0.1:${PORT}/health || exit 1

# Migrations run via lifespan in backend.app.main; Gunicorn + Uvicorn workers boot the API.
# WEB_CONCURRENCY drives worker count (set in fly.toml [env] or docker-compose).
CMD ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT} backend.app.main:app"]
