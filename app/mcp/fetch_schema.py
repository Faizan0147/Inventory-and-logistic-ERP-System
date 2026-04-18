import asyncpg
import json
async def get_table_schema(
    conn: asyncpg.Connection,
    table_name: str
):
    schema = {}
    rows = await conn.fetch(
        """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = $1
        ORDER BY ordinal_position;
        """,
        table_name
    )
    schema[table_name] = [dict(c) for c in rows]
    return json.dumps(schema)