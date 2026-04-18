"""
MCP Server — exposes 3 database tools via SSE.
Mounted inside FastAPI at /mcp in app/main.py.

Tools:
  1. list_tables()           → all table names
  2. fetch_schema(table)     → column definitions
  3. execute_sql_query(sql)  → run SQL with RAC enforcement
"""
from fastmcp import FastMCP
import json
from typing import Optional

from app.database import get_pool
from app.mcp.auth import get_user_from_fastmcp_request
from app.mcp.rac import apply_rac
from app.mcp.fetch_tables import fetch_tables
from app.mcp.fetch_schema import get_table_schema
from app.mcp.execute_query import execute_query

mcp = FastMCP("GodaamX")


@mcp.tool()
async def list_tables() -> str:
    """Returns all table names in the database. Call this first."""
    try:
        get_user_from_fastmcp_request()
    except ValueError as e:
        return json.dumps({"error": str(e)})

    pool = await get_pool()
    async with pool.acquire() as conn:
        return await fetch_tables(conn)


@mcp.tool()
async def fetch_schema(table_name: str) -> str:
    """Returns column definitions for a table. Call after list_tables."""
    try:
        get_user_from_fastmcp_request()
    except ValueError as e:
        return json.dumps({"error": str(e)})

    pool = await get_pool()
    async with pool.acquire() as conn:
        return await get_table_schema(conn, table_name)


@mcp.tool()
async def execute_sql_query(sql: str, params: Optional[list] = None) -> str:
    """
    Run a SQL query with automatic role-based access control.
    SUPERADMIN = full access. SUPPLIER = scoped to their supplier_id.
    DROP/ALTER/CREATE/TRUNCATE are always blocked.
    """
    try:
        user = get_user_from_fastmcp_request()
    except ValueError as e:
        return json.dumps({"error": str(e)})

    if params is None:
        params = []

    try:
        safe_sql, safe_params = apply_rac(sql, params, user)
    except PermissionError as e:
        return json.dumps({"error": f"Access denied: {e}"})

    pool = await get_pool()
    async with pool.acquire() as conn:
        try:
            result = await execute_query(conn, safe_sql, safe_params)
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"error": str(e)})
        
import uvicorn

if __name__ == "__main__":
    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=8001
    )