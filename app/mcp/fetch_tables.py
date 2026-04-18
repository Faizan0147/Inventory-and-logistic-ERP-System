import asyncpg
import json
async def fetch_tables(
    conn: asyncpg.Connection
): 
    rows = await conn.fetch(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE';
        """
    )
    return json.dumps({"tables": [row["table_name"] for row in rows]})