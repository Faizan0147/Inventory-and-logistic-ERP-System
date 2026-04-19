"""
LangChain tool wrappers around the existing MCP tools.

Each tool calls mcp.call_tool() in-process — identical to the custom agent,
but wrapped in LangChain's @tool decorator for automatic schema generation.

User context (ContextVar) must be set by the caller BEFORE the agent runs.
"""
import json
from typing import Optional

from langchain_core.tools import tool

from app.mcp.server import mcp


def _extract_text(result) -> str:
    """Extract text from an MCP CallToolResult."""
    content = getattr(result, "content", None)
    if isinstance(content, list):
        text_parts: list[str] = []
        for item in content:
            text_val = getattr(item, "text", None)
            if text_val:
                text_parts.append(text_val)
        if text_parts:
            return "\n".join(text_parts)
    if isinstance(content, str):
        return content
    return str(result)


# ── Tool definitions ────────────────────────────────────────────────────
# LangChain auto-generates the JSON schema from the function signature
# and docstring — no manual TOOL_DECLARATIONS needed.


@tool
async def list_tables() -> str:
    """Returns all database table names. Call this first to discover available tables."""
    try:
        result = await mcp.call_tool("list_tables", {})
        return _extract_text(result)
    except Exception as exc:
        return json.dumps({"error": str(exc)})


@tool
async def fetch_schema(table_name: str) -> str:
    """Returns column definitions for a given table. Call after list_tables."""
    try:
        result = await mcp.call_tool("fetch_schema", {"table_name": table_name})
        return _extract_text(result)
    except Exception as exc:
        return json.dumps({"error": str(exc)})


@tool
async def execute_sql_query(sql: str, params: Optional[list] = None) -> str:
    """Execute a SQL query with automatic role-based access control.
    SUPERADMIN gets full access. SUPPLIER is scoped to their supplier_id.
    DROP/ALTER/CREATE/TRUNCATE are always blocked."""
    try:
        args: dict = {"sql": sql}
        if params:
            args["params"] = params
        result = await mcp.call_tool("execute_sql_query", args)
        return _extract_text(result)
    except Exception as exc:
        return json.dumps({"error": str(exc)})


# Convenience list for the agent
ALL_TOOLS = [list_tables, fetch_schema, execute_sql_query]
