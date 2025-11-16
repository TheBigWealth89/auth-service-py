import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy import engine_from_config

from alembic import context

# Alembic Config object (from alembic.ini)
config = context.config

# prefer env var for DB URL (don't store secrets in alembic.ini)
DB_URL = os.getenv("DATABASE_URL")
if DB_URL:
    config.set_main_option("sqlalchemy.url", DB_URL)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ------------------ make project importable ------------------
# Compute project root (one level above the alembic/ folder)
here = os.path.abspath(os.path.dirname(__file__))      # .../alembic
project_root = os.path.abspath(os.path.join(here, ".."))  # project root

# Add project root to sys.path so absolute imports of your package work
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import Base using an absolute import (no relative imports)
# IMPORTANT: replace 'app.core.db' below if your module path differs
try:
    from app.core.db import Base
except Exception as exc:
    # helpful debug message to guide you
    raise ImportError(
        "Could not import Base from app.core.db. Make sure:\n"
        "  1) your project root (the folder containing 'app') is one level above alembic/\n"
        "  2) the module path is correct (app.core.db defines `Base`),\n"
        "  3) you run alembic from the project root (where alembic.ini lives).\n\n"
        "Original error: " + str(exc)
    ) from exc

target_metadata = Base.metadata
# -------------------------------------------------------------

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


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    from sqlalchemy.ext.asyncio import create_async_engine

    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
