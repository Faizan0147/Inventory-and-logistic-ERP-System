import asyncio
import asyncpg
from app.config import settings

# Connection pool — created once at startup, shared across requests
_pool: asyncpg.Pool | None = None
_pool_lock = asyncio.Lock()


async def create_pool():
    """Explicitly create the pool (used by FastAPI on startup)."""
    global _pool
    print("DATABASE_URL:", settings.DATABASE_URL)
    _pool = await asyncpg.create_pool(
        settings.DATABASE_URL,
        min_size=2,
        max_size=10,
        command_timeout=10,
    )


async def get_pool() -> asyncpg.Pool:
    """Returns the shared asyncpg connection pool, creating it on first call (lazy initialization)."""
    global _pool
    if _pool is None:
        async with _pool_lock:
            if _pool is None:
                print("DATABASE_URL:", settings.DATABASE_URL)
                _pool = await asyncpg.create_pool(
                    settings.DATABASE_URL,
                    min_size=2,
                    max_size=10,
                    command_timeout=10,
                )
    return _pool


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def get_connection():
    """FastAPI dependency: yields a single connection from the pool."""
    async with _pool.acquire() as conn:
        yield conn
