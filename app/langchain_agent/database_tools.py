"""
Direct database tools for LangChain agent.
These functions access the database directly while reusing security logic
from app.langchain_agent.query_checks for role-based access control (RB AC).
User context is provided via ContextVar (set by chat.py).
"""
import asyncpg
import json
from datetime import date, datetime
from decimal import Decimal
from contextvars import ContextVar

from app.database import get_pool
from app.langchain_agent.query_checks import apply_query_checks


# ContextVar for user context
_CURRENT_USER: ContextVar[dict | None] = ContextVar("current_user", default=None)


def get_current_user() -> dict:
    """Retrieve user from context. Raises ValueError if not set."""
    user = _CURRENT_USER.get()
    if not user:
        raise ValueError("No user context set for database tool")
    return user


def set_user_context(user: dict):
    """Set user context for database tools. Returns a token for cleanup."""
    return _CURRENT_USER.set(user)


def reset_user_context(token):
    """Reset user context after tool execution."""
    _CURRENT_USER.reset(token)


def _serialize(obj):
    """JSON serializer for asyncpg types not handled by default."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    return str(obj)


async def list_tables_direct() -> str:
    """Returns all database table names. No parameters needed."""
    try:
        user = get_current_user()
    except ValueError as e:
        return json.dumps({"error": str(e)})

    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE';
                """
            )
            return json.dumps({"tables": [row["table_name"] for row in rows]})
    except Exception as exc:
        return json.dumps({"error": f"Failed to fetch tables: {exc}"})


async def fetch_schema_direct(table_name: str) -> str:
    """Returns column definitions for a given table."""
    try:
        user = get_current_user()
    except ValueError as e:
        return json.dumps({"error": str(e)})

    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
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
    except Exception as exc:
        return json.dumps({"error": f"Failed to fetch schema for {table_name}: {exc}"})


async def execute_sql_query_direct(sql: str, params: list = None) -> str:
    """
    Execute a SQL query with automatic role-based access control.
    SUPERADMIN gets full access. SUPPLIER is scoped to their supplier_id.
    DROP/ALTER/CREATE/TRUNCATE are always blocked.
    """
    try:
        user = get_current_user()
    except ValueError as e:
        return json.dumps({"error": str(e)})

    if params is None:
        params = []

    try:
        # Apply RAC enforcement
        safe_sql, safe_params = apply_query_checks(sql, params, user)
    except PermissionError as e:
        return json.dumps({"error": f"Access denied: {e}"})

    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            sql_clean = safe_sql.strip()

            if sql_clean.upper().startswith("SELECT"):
                
                # SELECT query — return rows
                rows = await conn.fetch(sql_clean, *safe_params)
                data = [dict(row) for row in rows]
                
                # Serialize asyncpg-specific types (date, Decimal, etc.)
                serialized = json.loads(json.dumps(data, default=_serialize))
                return json.dumps({"rows": serialized, "row_count": len(serialized)})
            
            else:
                # DML: INSERT / UPDATE / DELETE
                status = await conn.execute(sql_clean, *safe_params)
                # status string e.g. "INSERT 0 1", "UPDATE 3", "DELETE 2"
                parts = status.split()
                row_count = int(parts[-1]) if parts and parts[-1].isdigit() else 0
                return json.dumps({"status": status, "row_count": row_count})
    except Exception as exc:
        return json.dumps({"error": str(exc)})
