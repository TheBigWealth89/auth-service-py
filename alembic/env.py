# alembic/env.py — async-ready, loads .env, ensures models are imported
import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

config = context.config

# --- Make project importable (so absolute imports like "app.core.db" work) ---
here = os.path.abspath(os.path.dirname(__file__))      # alembic/
project_root = os.path.abspath(os.path.join(here, ".."))  # project root
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Load .env so Alembic sees same env vars as your app (optional but helpful) ---
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(project_root, ".env"))
except Exception:
    pass

# Prefer DB URL from environment (DATABASE_URL), but fall back to alembic.ini
env_db_url = os.getenv("DATABASE_URL")
if env_db_url and env_db_url.strip():
    config.set_main_option("sqlalchemy.url", env_db_url)

# Validate the URL early and print debug info
url_candidate = config.get_main_option("sqlalchemy.url")
print("DEBUG: alembic will use sqlalchemy.url ->", repr(url_candidate))
if not url_candidate or url_candidate.strip().startswith("driver://"):
    raise RuntimeError(
        "DATABASE URL not set or invalid. Set DATABASE_URL env var (e.g. "
        "'postgresql+asyncpg://user:pass@host:port/dbname') or update sqlalchemy.url in alembic.ini."
    )
try:
    make_url(url_candidate)
except Exception as exc:
    raise RuntimeError(f"Could not parse DATABASE_URL: {exc}\nValue was: {repr(url_candidate)}") from exc

# --- Import Base and ensure your model modules are imported so they register with Base.metadata ---
try:
    # import the module that defines Base (adjust to your path)
    from app.core.db import Base
except Exception as exc:
    raise ImportError(
        "Could not import Base from app.core.db. Ensure the project root contains 'app' and "
        "that app/core/db.py defines Base = declarative_base().\n"
        f"Original error: {exc}"
    ) from exc

# Force import of model modules so metadata is populated.
# Replace these with modules where your models live.
try:
    import app.models.user_model   # <-- adjust this to your models module(s)
    import app.models.refresh_token_model
    import app.models.email_verification_model
    import app.models.password_reset_tokens
    # import app.models.other_model  # add more if you have additional model files
except Exception:
    # If imports fail, let it surface below when we inspect metadata
    pass

# Debug: show which tables Alembic sees
print("DEBUG: tables known to metadata:", list(Base.metadata.tables.keys()))

target_metadata = Base.metadata

# --- migration runner functions (async-enabled) ---
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
