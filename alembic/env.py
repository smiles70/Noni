"""Alembic environment configured to read DATABASE_URL from settings.

All model modules must be imported here so their tables register with
`Base.metadata`. New models added in the future MUST be imported below
or autogenerate will not see them.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from backend.core.config import settings
from backend.core.database import Base

# Import models so they're registered on Base.metadata.
# NOTE: every new domain model module MUST be imported here, otherwise
# alembic autogenerate will not see it.
from backend.models import telemetry as _telemetry  # noqa: F401
from backend.models import accounts as _accounts  # noqa: F401
from backend.models import auth as _auth  # noqa: F401
from backend.models import billing as _billing  # noqa: F401
from backend.models import learning as _learning  # noqa: F401
from backend.models import governance as _governance  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# NB: we intentionally skip fileConfig(config.config_file_name). The
# logging section in alembic.ini sets the root logger to WARNING, which
# would override uvicorn's INFO-level access logs and our own
# logger.info() calls (e.g. clerk_user_lookup_* in auth_provider.py)
# after `run_migrations()` runs at FastAPI lifespan startup. Alembic's
# own migration messages still print via Python's default handler, which
# uvicorn already configures.
_ = fileConfig  # imported for type checkers; intentionally unused

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
