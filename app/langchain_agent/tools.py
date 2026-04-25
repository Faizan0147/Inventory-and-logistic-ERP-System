"""
LangChain tool wrappers for direct database access.

Wrapped in LangChain's @tool decorator for automatic schema generation
and function calling. User context (ContextVar) is set by chat.py before
the agent runs.
"""
from typing import Optional
from langchain_core.tools import tool
from app.langchain_agent.database_tools import (
    list_tables_direct,
    fetch_schema_direct,
    execute_sql_query_direct,
)


# ── Tool definitions ────────────────────────────────────────────────────
# LangChain auto-generates the JSON schema from the function signature
# and docstring — no manual TOOL_DECLARATIONS needed.


@tool
async def list_tables() -> str:
    """Returns all database table names. Call this first to discover available tables."""
    return await list_tables_direct()


@tool
async def fetch_schema(table_name: str) -> str:
    """Returns column definitions for a given table. Call after list_tables."""
    return await fetch_schema_direct(table_name)


@tool
async def execute_sql_query(sql: str, params: Optional[list] = None) -> str:
    """Execute a SQL query with automatic role-based access control.
    SUPERADMIN gets full access. SUPPLIER is scoped to their supplier_id.
    DROP/ALTER/CREATE/TRUNCATE are always blocked."""
    return await execute_sql_query_direct(sql, params or [])


# Convenience list for the agent
ALL_TOOLS = [list_tables, fetch_schema, execute_sql_query]
