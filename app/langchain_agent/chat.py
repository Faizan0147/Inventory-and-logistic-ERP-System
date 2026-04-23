"""
LangChain agent controller — drop-in alternative to app.controllers.chat.

Uses ChatOpenAI pointed at Groq's OpenAI-compatible endpoint,
with LangGraph's create_react_agent (the modern LangChain agent API).

Direct database tools (bypasses MCP server for better performance).

Compare with app/controllers/chat.py (the custom 130-line agent loop).
"""
from typing import Any

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from app.config import settings
from app.langchain_agent.database_tools import set_user_context, reset_user_context
from app.langchain_agent.tools import ALL_TOOLS


# ── Same system prompt as the custom agent ──────────────────────────────
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


async def chat_with_langchain(
    prompt: str,
    user: dict,
    debug: bool = False,
) -> dict[str, Any]:
    """
    LangChain equivalent of chat_with_mcp().

    Same LLM (Groq Llama), same tools (direct DB access), same system prompt.
    The only difference: LangGraph handles the tool-calling loop, and we use
    direct database functions instead of MCP server.
    """
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing in .env")

    # ChatOpenAI pointed at Groq's OpenAI-compatible API
    llm = ChatOpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
        model=settings.GROQ_MODEL,
        temperature=0.2,
    )

    # Create the react agent (LangGraph-based, replaces the old AgentExecutor)
    agent = create_react_agent(
        model=llm,
        tools=ALL_TOOLS,
        prompt=SYSTEM_PROMPT,
    )

    # Set user context (ContextVar) so database tools see the authenticated user.
    # This is safe for concurrent requests — each asyncio Task has its own copy.
    token = set_user_context(user)
    try:
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": prompt}]},
            config={"recursion_limit": settings.TOOL_CALL_MAX_STEPS},
        )

        # Extract the final AI message from the conversation history
        messages = result.get("messages", [])
        reply = ""
        for msg in reversed(messages):
            # Find the last AI message that isn't a tool call
            if hasattr(msg, "content") and getattr(msg, "type", None) == "ai":
                if msg.content and not getattr(msg, "tool_calls", None):
                    reply = msg.content
                    break

        if not reply:
            reply = "I could not generate a response."

        out: dict[str, Any] = {"reply": reply}

        if debug:
            # Serialize the full message history for inspection
            debug_messages = []
            for msg in messages:
                entry = {
                    "type": getattr(msg, "type", "unknown"),
                    "content": getattr(msg, "content", ""),
                }
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    entry["tool_calls"] = [
                        {"name": tc["name"], "args": tc["args"]}
                        for tc in msg.tool_calls
                    ]
                if hasattr(msg, "name") and msg.name:
                    entry["tool_name"] = msg.name
                debug_messages.append(entry)

            out["debug"] = {
                "model": settings.GROQ_MODEL,
                "framework": "langgraph",
                "messages": debug_messages,
            }

        return out

    except Exception as exc:
        raise ValueError(f"LangChain agent error: {exc}")
    finally:
        reset_user_context(token)
