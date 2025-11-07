from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
# from sqlalchemy import text

# import database url form config
from .config import DATABASE_URL

# Create async engine connection pool + SQL compilations
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Prints SQL to stdout for developing
    future=True,
)


# Async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # This avoid needing to re-fetch objects after commit
    autoflush=False,        # Disable auth flush for explicit control
    future=True
)

# Base class for ORM models
Base = declarative_base()
