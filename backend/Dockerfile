# syntax=docker/dockerfile:1.6
# Multi-stage build for the Noni backend.
# Stage 1: install dependencies into a virtualenv.
# Stage 2: copy the venv + code into a slim runtime image.
# Build context is the repo root (so we can copy alembic/, backend/).

# ---------- Stage 1: builder ----------
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV=/opt/venv

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

# ---------- Stage 2: runtime ----------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# Runtime needs libpq for psycopg2.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --system --create-home --uid 10001 noni

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY --chown=noni:noni backend ./backend
COPY --chown=noni:noni alembic ./alembic
COPY --chown=noni:noni alembic.ini ./alembic.ini

USER noni
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/health || exit 1

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "3", "--bind", "0.0.0.0:8000", "backend.app.main:app"]
