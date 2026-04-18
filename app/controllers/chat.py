import json
import asyncio
from typing import Any

from groq import AsyncGroq

from app.config import settings
from app.mcp.auth import set_mcp_user_context, reset_mcp_user_context
from app.mcp.server import mcp


TOOL_DECLARATIONS = [
    {
        "name": "list_tables",
        "description": "Returns all database table names.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "fetch_schema",
        "description": "Returns column definitions for a table.",
        "parameters": {
            "type": "object",
            "properties": {
                "table_name": {"type": "string"},
            },
            "required": ["table_name"],
        },
    },
    {
        "name": "execute_sql_query",
        "description": "Execute an SQL query with role-based access control.",
        "parameters": {
            "type": "object",
            "properties": {
                "sql": {"type": "string"},
                "params": {
                    "type": "array",
                    "items": {},
                },
            },
            "required": ["sql"],
        },
    },
]

SYSTEM_PROMPT = (
    "You are a helpful ERP data assistant. You have access to tools for database exploration "
    "and SQL execution — use them when the user asks about tables, schemas, or data.\n\n"

    "## Core Rules\n"
    "- Never fabricate table names, column names, or data.\n"
    "- If a tool returns an error, explain it in plain language and suggest a next step.\n\n"

    "## Data Privacy\n"
    "- Never expose internal/technical fields such as: IDs, deleted status, is_active, "
    "created_by, updated_by, created_at, or updated_at — even if they exist in the schema.\n\n"

    "## Query Workflow\n"
    "- When a user requests data, generate the SQL query, inform the user by saying "
    "'Executing the following query:' followed by the query, then immediately execute it.\n\n"

    "## Response Style\n"
    "- Always respond in a conversational, business-friendly tone.\n"
    "- Do not list all available tables unless explicitly asked.\n"
    "- Keep answers concise and focused on what the user actually needs.\n"
)



async def _invoke_mcp_tool(tool_name: str, arguments: dict[str, Any], user: dict) -> str:
    token = set_mcp_user_context(user)
    try:
        result = await mcp.call_tool(tool_name, arguments or {})
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
    except Exception as exc:
        return json.dumps({"error": str(exc)})
    finally:
        reset_mcp_user_context(token)


async def chat_with_mcp(prompt: str, user: dict, debug: bool = False) -> dict[str, Any]:
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing in .env")

    client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    # Build initial messages for Groq
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    # Convert TOOL_DECLARATIONS to Groq 'tools' format
    tools = []
    for t in TOOL_DECLARATIONS:
        fn = {
            "type": "function",
            "function": {
                "name": t.get("name"),
                "description": t.get("description"),
                "parameters": t.get("parameters", {}),
            },
        }
        tools.append(fn)

    captured_tool_calls: list[dict[str, Any]] = []

    # Loop: ask model, execute any tool calls, feed results back, then get final answer.
    # Critical: always append the assistant message BEFORE tool results so the model
    # sees its own prior decisions and stops re-calling the same tools.
    for _ in range(settings.TOOL_CALL_MAX_STEPS):
        try:
            resp = await client.chat.completions.create(
                messages=messages,
                model=settings.GROQ_MODEL,
                tools=tools,
                tool_choice="auto",
                temperature=0.2,
            )
        except Exception as exc:
            raise ValueError(f"Groq API error: {exc}")

        choices = getattr(resp, "choices", []) or []
        if not choices:
            raise ValueError("Groq returned no choices")

        choice = choices[0]
        msg = getattr(choice, "message", None)
        tool_calls = getattr(msg, "tool_calls", None) or []
        content = getattr(msg, "content", None) or ""

        # No tool calls → model is done; return the text reply
        if not tool_calls:
            final_text = content.strip() if isinstance(content, str) else str(content)
            if not final_text:
                final_text = "I could not generate a response."
            out = {"reply": final_text}
            if debug:
                out["debug"] = {
                    "model": settings.GROQ_MODEL,
                    "tool_calls": captured_tool_calls,
                }
            return out

        # Step 1: append the ASSISTANT message (with tool_calls) so the model
        # sees its own decisions in subsequent turns and doesn't loop.
        assistant_msg: dict[str, Any] = {"role": "assistant", "content": content or ""}
        serialised_tool_calls = []
        for tc in tool_calls:
            fn = getattr(tc, "function", None)
            serialised_tool_calls.append({
                "id": getattr(tc, "id", ""),
                "type": "function",
                "function": {
                    "name": getattr(fn, "name", "") if fn else "",
                    "arguments": getattr(fn, "arguments", "") if fn else "",
                },
            })
        assistant_msg["tool_calls"] = serialised_tool_calls
        messages.append(assistant_msg)

        # Step 2: run each tool and append a role="tool" message with tool_call_id
        for tc in tool_calls:
            function = getattr(tc, "function", None)
            if not function:
                continue
            tool_name = getattr(function, "name", "")
            args_str = getattr(function, "arguments", "") or ""
            tc_id = getattr(tc, "id", tool_name)
            try:
                args = json.loads(args_str) if args_str else {}
            except Exception:
                args = {}

            tool_result = await _invoke_mcp_tool(tool_name, args, user)
            captured_tool_calls.append({"name": tool_name, "arguments": args, "result": tool_result})

            # role="tool" + tool_call_id is required by Groq/OpenAI protocol
            messages.append({
                "role": "tool",
                "tool_call_id": tc_id,
                "content": tool_result,
            })

    out = {"reply": f"I reached the tool-call step limit ({settings.TOOL_CALL_MAX_STEPS}). Please refine your request."}
    if debug:
        out["debug"] = {"model": settings.GROQ_MODEL, "tool_calls": captured_tool_calls}
    return out
