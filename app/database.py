import asyncpg
from app.config import settings

# Connection pool — created once at startup, shared across requests
_pool: asyncpg.Pool | None = None


async def create_pool():
    global _pool
    print("DATABASE_URL:", settings.DATABASE_URL)
    _pool = await asyncpg.create_pool(
        settings.DATABASE_URL,
        min_size=2,
        max_size=10,
        command_timeout=10,
    )

    

async def close_pool():
    global _pool
    if _pool:
        await _pool.close()


async def get_connection():
    """FastAPI dependency: yields a single connection from the pool."""
    async with _pool.acquire() as conn:
        yield conn
