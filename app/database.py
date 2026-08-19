import os
import logging
from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncAttrs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("senacontigo.database")

class Base(AsyncAttrs, DeclarativeBase):
    """Base declarative class for all SQLAlchemy 2.0 models."""
    pass

DEFAULT_PG_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/senacontigo"
DEFAULT_SQLITE_ASYNC_URL = "sqlite+aiosqlite:///./senacontigo.db"
DEFAULT_SQLITE_SYNC_URL = "sqlite:///./senacontigo.db"

RAW_DB_URL = os.getenv("DATABASE_URL", DEFAULT_PG_URL)


def resolve_db_urls(raw_url: str):
    """
    Given a connection string, returns a tuple of (async_url, sync_url).
    """
    if raw_url.startswith("postgresql+asyncpg://"):
        async_url = raw_url
        sync_url = raw_url.replace("postgresql+asyncpg://", "postgresql://")
    elif raw_url.startswith("postgresql://"):
        sync_url = raw_url
        async_url = raw_url.replace("postgresql://", "postgresql+asyncpg://")
    elif raw_url.startswith("sqlite+aiosqlite://"):
        async_url = raw_url
        sync_url = raw_url.replace("sqlite+aiosqlite://", "sqlite://")
    elif raw_url.startswith("sqlite://"):
        sync_url = raw_url
        async_url = raw_url.replace("sqlite://", "sqlite+aiosqlite://")
    else:
        async_url = raw_url
        sync_url = raw_url
    return async_url, sync_url


def create_engines_with_fallback(raw_url: str):
    """
    Attempts to initialize PostgreSQL engines. If connection fails or PostgreSQL is inactive,
    falls back to SQLite (async: aiosqlite, sync: sqlite3).
    """
    async_url, sync_url = resolve_db_urls(raw_url)

    if "postgresql" in sync_url:
        try:
            logger.info(f"Probando conexión con PostgreSQL: {sync_url}")
            test_engine = create_engine(sync_url, connect_args={"connect_timeout": 2})
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            test_engine.dispose()
            logger.info("Conexión exitosa a PostgreSQL.")
            return (
                create_async_engine(async_url, echo=False, future=True),
                create_engine(sync_url, echo=False, future=True)
            )
        except Exception as err:
            logger.warning(f"PostgreSQL no está activo o falló la conexión ({err}). Usando fallback a SQLite.")
            async_url = DEFAULT_SQLITE_ASYNC_URL
            sync_url = DEFAULT_SQLITE_SYNC_URL

    logger.info(f"Inicializando motores de base de datos en SQLite: {sync_url}")
    async_eng = create_async_engine(async_url, echo=False, future=True)
    sync_eng = create_engine(sync_url, echo=False, future=True, connect_args={"check_same_thread": False})
    return async_eng, sync_eng


async_engine, sync_engine = create_engines_with_fallback(RAW_DB_URL)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    expire_on_commit=False,
    autoflush=False
)

# Compatibility Aliases
engine = sync_engine
SessionLocal = SyncSessionLocal


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency generator for FastAPI / Async context."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_db() -> Generator[Session, None, None]:
    """Dependency generator for Sync context."""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db_sync():
    """Create all tables synchronously."""
    Base.metadata.create_all(bind=sync_engine)


async def init_db():
    """Create all tables asynchronously."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
