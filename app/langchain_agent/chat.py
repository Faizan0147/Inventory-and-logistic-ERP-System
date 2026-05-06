import asyncio
import logging
from typing import Any

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from app.config import settings
from app.langchain_agent.database_tools import set_user_context, reset_user_context
from app.langchain_agent.tools import ALL_TOOLS
from app.repositories import chat_repo

logger = logging.getLogger(__name__)


# ── System Prompt ────────────────────────────────────────────────

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


# ── Title Generation ─────────────────────────────────────────────

async def _generate_title(conversation_id: str, user_id: str, first_message: str) -> None:
    """
    Background task: asks the LLM for a short title based on the first user message,
    then saves it to the database. Failures are logged but never surface to the user.
    """
    try:
        llm = ChatOpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
            model=settings.GROQ_MODEL,
            temperature=0.3,
        )
        response = await llm.ainvoke([
            {
                "role": "user",
                "content": (
                    f"Generate a short 4-6 word title for a conversation that starts with: "
                    f"'{first_message[:300]}'. "
                    f"Reply with ONLY the title text, no quotes, no punctuation at the end."
                ),
            }
        ])
        title = response.content.strip().strip('"').strip("'")[:200]
        if title:
            await chat_repo.update_title(conversation_id, user_id, title)
            logger.info("Auto-titled conversation %s: %s", conversation_id, title)
    except Exception as exc:
        logger.warning("Title generation failed for %s: %s", conversation_id, exc)


# ── Main Chat Function ──────────────────────────────────────────


async def chat_with_langchain(
    prompt: str,
    user: dict,
    conversation_id: str | None = None,
    debug: bool = False,
) -> dict[str, Any]:

    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing in .env")

    user_id = user["user_id"]

    # ── 1. Create or validate conversation ───────────────────────
    is_new_conversation = False

    if conversation_id is None:
        # New conversation — create it in the database
        conv = await chat_repo.create_conversation(user_id)
        conversation_id = conv["conversation_id"]
        is_new_conversation = True
    else:
        # Existing conversation — verify ownership
        conv = await chat_repo.get_conversation(conversation_id, user_id)
        if not conv:
            raise ValueError("Conversation not found or access denied.")

    # ── 2. Load message history from database ────────────────────
    db_messages = await chat_repo.get_messages(conversation_id, user_id)
    history = [{"role": m["role"], "content": m["content"]} for m in db_messages]
    messages = history + [{"role": "user", "content": prompt}]

    # ── 3. Save user message to DB BEFORE calling LLM ────────────
    await chat_repo.add_message(conversation_id, "user", prompt)

    # ── 4. Call the LangGraph agent ──────────────────────────────
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

    token = set_user_context(user)
    try:
        result = await agent.ainvoke(
            {"messages": messages},
            config={"recursion_limit": settings.TOOL_CALL_MAX_STEPS},
        )

        # ── 5. Extract the final AI reply ────────────────────────
        result_messages = result.get("messages", [])
        reply = ""
        for msg in reversed(result_messages):
            if hasattr(msg, "content") and getattr(msg, "type", None) == "ai":
                if msg.content and not getattr(msg, "tool_calls", None):
                    reply = msg.content
                    break

        if not reply:
            reply = "I could not generate a response."

        # ── 6. Save assistant reply to DB ────────────────────────
        await chat_repo.add_message(conversation_id, "assistant", reply)

        # ── 7. Auto-generate title for new conversations ─────────
        if is_new_conversation:
            asyncio.create_task(_generate_title(conversation_id, user_id, prompt))

        # ── 8. Build response ────────────────────────────────────
        out: dict[str, Any] = {
            "reply": reply,
            "conversation_id": conversation_id,
        }

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
