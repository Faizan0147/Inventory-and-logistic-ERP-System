"""
Repository for chat conversations and messages.
Handles all database operations for the conversational memory system.
"""

import logging
from uuid import uuid4
from typing import Optional

from app.database import get_pool

logger = logging.getLogger(__name__)


# ── Conversation Operations ──────────────────────────────────────


async def create_conversation(user_id: str) -> dict:
    """Create a new conversation for a user. Returns the conversation dict."""
    pool = await get_pool()
    conversation_id = str(uuid4())

    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO chat_conversations
                    (conversation_id, user_id)
                VALUES ($1, $2)
                RETURNING conversation_id, user_id, title, is_titled,
                          message_count, created_at, updated_at
                """,
                conversation_id,
                user_id,
            )
            return dict(row)

    except Exception as e:
        logger.error("create_conversation: %s", e)
        raise RuntimeError(f"Failed to create conversation: {e}")


async def list_conversations(user_id: str) -> list[dict]:
    """
    List all non-deleted conversations for a user.
    Returns lightweight metadata for sidebar rendering — no message content.
    Ordered by most recently updated first.
    """
    pool = await get_pool()

    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT conversation_id, title, message_count,
                       created_at, updated_at
                FROM   chat_conversations
                WHERE  user_id = $1
                  AND  deleted = FALSE
                ORDER BY updated_at DESC
                """,
                user_id,
            )
            return [dict(r) for r in rows]

    except Exception as e:
        logger.error("list_conversations(%s): %s", user_id, e)
        raise RuntimeError(f"Failed to list conversations: {e}")


async def get_conversation(
    conversation_id: str, user_id: str
) -> Optional[dict]:
    """
    Get a single conversation's metadata.
    Returns None if not found or not owned by the user.
    """
    pool = await get_pool()

    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT conversation_id, user_id, title, is_titled,
                       message_count, created_at, updated_at
                FROM   chat_conversations
                WHERE  conversation_id = $1
                  AND  user_id = $2
                  AND  deleted = FALSE
                """,
                conversation_id,
                user_id,
            )
            return dict(row) if row else None

    except Exception as e:
        logger.error("get_conversation(%s): %s", conversation_id, e)
        raise RuntimeError(f"Failed to get conversation: {e}")


async def update_title(
    conversation_id: str, user_id: str, title: str
) -> bool:
    """
    Update the title of a conversation.
    Sets is_titled = TRUE to prevent auto-titling from overwriting a manual title.
    Returns True if a row was updated, False if conversation not found / not owned.
    """
    pool = await get_pool()

    try:
        async with pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE chat_conversations
                SET    title     = $1,
                       is_titled = TRUE,
                       updated_at = CURRENT_TIMESTAMP
                WHERE  conversation_id = $2
                  AND  user_id = $3
                  AND  deleted = FALSE
                """,
                title[:200],  # enforce max length
                conversation_id,
                user_id,
            )
            return result == "UPDATE 1"

    except Exception as e:
        logger.error("update_title(%s): %s", conversation_id, e)
        raise RuntimeError(f"Failed to update conversation title: {e}")


async def delete_conversation(
    conversation_id: str, user_id: str
) -> bool:
    """
    Soft-delete a conversation and all its messages.
    Returns True if a row was deleted, False if not found / not owned.
    """
    pool = await get_pool()

    try:
        async with pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE chat_conversations
                SET    deleted    = TRUE,
                       updated_at = CURRENT_TIMESTAMP
                WHERE  conversation_id = $1
                  AND  user_id = $2
                  AND  deleted = FALSE
                """,
                conversation_id,
                user_id,
            )
            return result == "UPDATE 1"

    except Exception as e:
        logger.error("delete_conversation(%s): %s", conversation_id, e)
        raise RuntimeError(f"Failed to delete conversation: {e}")


# ── Message Operations ───────────────────────────────────────────


async def add_message(
    conversation_id: str, role: str, content: str
) -> dict:
    """
    Add a message to a conversation.
    The DB trigger automatically updates the conversation's
    updated_at timestamp and message_count.
    """
    pool = await get_pool()
    message_id = str(uuid4())

    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO chat_messages
                    (message_id, conversation_id, role, content)
                VALUES ($1, $2, $3, $4)
                RETURNING message_id, conversation_id, role, content, created_at
                """,
                message_id,
                conversation_id,
                role,
                content,
            )
            return dict(row)

    except Exception as e:
        logger.error("add_message(%s, %s): %s", conversation_id, role, e)
        raise RuntimeError(f"Failed to add message: {e}")


async def get_messages(
    conversation_id: str, user_id: str
) -> list[dict]:
    """
    Get all messages for a conversation, ordered chronologically.
    Includes an ownership check — the conversation must belong to the user.
    """
    pool = await get_pool()

    try:
        async with pool.acquire() as conn:
            # First verify the user owns this conversation
            owner_check = await conn.fetchval(
                """
                SELECT 1 FROM chat_conversations
                WHERE conversation_id = $1
                  AND user_id = $2
                  AND deleted = FALSE
                """,
                conversation_id,
                user_id,
            )

            if not owner_check:
                return []

            rows = await conn.fetch(
                """
                SELECT message_id, role, content, created_at
                FROM   chat_messages
                WHERE  conversation_id = $1
                ORDER BY created_at ASC
                """,
                conversation_id,
            )
            return [dict(r) for r in rows]

    except Exception as e:
        logger.error("get_messages(%s): %s", conversation_id, e)
        raise RuntimeError(f"Failed to get messages: {e}")
