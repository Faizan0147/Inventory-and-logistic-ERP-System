from typing import Any
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from app.config import settings
from app.langchain_agent.database_tools import set_user_context, reset_user_context
from app.langchain_agent.tools import ALL_TOOLS

# In-memory conversation history store: { session_id: [messages] }
_conversation_store: dict[str, list[dict]] = {}


# ──system prompt ──────────────────────────────
SYSTEM_PROMPT = (
    "You are a helpful ERP data assistant. You have access to tools for database exploration "
    "and SQL execution — use them when the user asks about tables, schemas, or data.\n\n"

    "## Core Rules\n"
    "- Never fabricate table names, column names, or data.\n"
    "- If a tool returns an error, explain it in plain language and suggest a next step.\n\n"

    "## Data Privacy\n"
    "- Never expose internal/technical fields such as: IDs, deleted status, is_active, "
    "created_by, updated_by, created_at, or updated_at — even if they exist in the schema.\n\n"

    "## Automatic Data Scoping (IMPORTANT)\n"
    "- The system automatically filters data based on the user's role and permissions.\n"
    "- For SUPPLIER users: queries to all tables are automatically scoped to their user_id — "
    "you do NOT need to add user_id filters or ask the user for their user_id. "
    "Just write the query naturally (e.g., 'SELECT COUNT(*) FROM invoices WHERE status = \\'open\\'') "
    "and the system handles the rest.\n"
    "- For SUPERADMIN users: full access to all data without restrictions.\n"
    "- Never mention user_id filtering to the user — it happens transparently in the background.\n\n"

    "## Query Workflow\n"
    "- When a user requests data, generate the SQL query, inform the user by saying "
    "'Executing the following query:' followed by the query, then immediately execute it.\n"
    "- Show the user the clean query WITHOUT any supplier_id filters (those are added automatically).\n\n"

    "## Response Style\n"
    "- Always respond in a conversational, business-friendly tone.\n"
    "- Do not list all available tables unless explicitly asked.\n"
    "- Keep answers concise and focused on what the user actually needs.\n"
)


def clear_session(session_id: str) -> None:
    """Clear conversation history for a session."""
    _conversation_store.pop(session_id, None)


async def chat_with_langchain(
    prompt: str,
    user: dict,
    session_id: str | None = None,
    debug: bool = False,
) -> dict[str, Any]:

    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing in .env")

    llm = ChatOpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
        model=settings.GROQ_MODEL,
        temperature=0.2,
    )

    agent = create_react_agent(
        model=llm,
        tools=ALL_TOOLS,
        prompt=SYSTEM_PROMPT,
    )

    # Build message history
    history = _conversation_store.get(session_id, []) if session_id else []
    messages = history + [{"role": "user", "content": prompt}]

    token = set_user_context(user)
    try:
        result = await agent.ainvoke(
            {"messages": messages},
            config={"recursion_limit": settings.TOOL_CALL_MAX_STEPS},
        )

        # Extract the final AI message
        result_messages = result.get("messages", [])
        reply = ""
        for msg in reversed(result_messages):
            if hasattr(msg, "content") and getattr(msg, "type", None) == "ai":
                if msg.content and not getattr(msg, "tool_calls", None):
                    reply = msg.content
                    break

        if not reply:
            reply = "I could not generate a response."

        # Persist updated history for this session
        if session_id:
            _conversation_store[session_id] = messages + [
                {"role": "assistant", "content": reply}
            ]

        out: dict[str, Any] = {"reply": reply}

        if debug:
            debug_messages = []
            for msg in result_messages:
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
