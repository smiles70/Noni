"""Spin up a local backend with an embedded PostgreSQL instance for
load/smoke testing without Docker or a system Postgres installation."""

import atexit
import os
import subprocess
import sys
import tempfile
import time

# Ensure imports resolve from the repository root.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import embedded_postgres
from sqlalchemy import text


def main() -> int:
    pgdata = tempfile.mkdtemp(prefix="noni-load-pg-")
    pg = embedded_postgres.get_server(pgdata, cleanup_mode="stop")
    pg.__enter__()
    atexit.register(pg.cleanup)

    uri = pg.get_uri()
    os.environ["DATABASE_URL"] = uri
    os.environ["DATABASE_URL_DIRECT"] = uri
    os.environ["AUTH_PROVIDER"] = "mock"
    os.environ["PAYMENT_PROVIDER"] = "mock"
    os.environ["SECRET_KEY"] = "test-secret-key-at-least-32-characters"
    os.environ["SESSION_SECRET"] = "test-session-secret-at-least-32-characters"

    # Create schema from SQLAlchemy metadata (no pgcrypto extension required).
    from backend.core.database import Base, engine
    from backend.tasks.celery_app import app as _  # noqa: F401

    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS citext"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

    # Start uvicorn in a subprocess.
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "warning"],
        env=os.environ.copy(),
    )
    atexit.register(proc.terminate)

    # Wait for health endpoint.
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            import urllib.request
            with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2) as resp:
                if resp.status == 200:
                    print("Backend ready at http://127.0.0.1:8000")
                    break
        except Exception:
            time.sleep(0.5)
    else:
        print("Backend failed to start")
        proc.terminate()
        return 1

    # Keep alive until interrupted.
    try:
        while proc.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        proc.terminate()
        proc.wait(timeout=10)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
