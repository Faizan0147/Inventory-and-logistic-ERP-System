import asyncpg
import json
from datetime import date, datetime
from decimal import Decimal


def _serialize(obj):
    """JSON serializer for asyncpg types not handled by default."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    return str(obj)


async def execute_query(
    conn: asyncpg.Connection,
    sql: str,
    params: list = None,
) -> dict:
    """
    Executes a SQL statement and returns a dict result.

    SELECT  → {"rows": [...], "row_count": N}
    DML     → {"status": "UPDATE 3", "row_count": 3}
    """
    if params is None:
        params = []

    sql = sql.strip()

    if sql.upper().startswith("SELECT"):
        rows = await conn.fetch(sql, *params)
        data = [dict(row) for row in rows]
        
        
        # Serialize asyncpg-specific types (date, Decimal, etc.)
        serialized = json.loads(json.dumps(data, default=_serialize))
        return {"rows": serialized, "row_count": len(serialized)}
    
    
    else:
        
        # DML: INSERT / UPDATE / DELETE
        status = await conn.execute(sql, *params)
        # status string e.g. "INSERT 0 1", "UPDATE 3", "DELETE 2"
        parts = status.split()
        row_count = int(parts[-1]) if parts and parts[-1].isdigit() else 0
        return {"status": status, "row_count": row_count}