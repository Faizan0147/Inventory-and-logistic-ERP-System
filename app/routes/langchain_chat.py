from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.langchain_agent.chat import chat_with_langchain
from app.dto.chat import (
    ChatRequest,
    ChatResponse,
    ConversationListItem,
    MessageItem,
    UpdateTitleRequest,
)
from app.repositories import chat_repo
from app.utils.dependencies import get_current_user

router = APIRouter()

CurrentUser = Annotated[dict, Depends(get_current_user)]


# ── Chat ─────────────────────────────────────────────────────────


@router.post("/message", response_model=ChatResponse)
async def send_message(
    body: ChatRequest,
    current_user: CurrentUser,
    debug: bool = Query(default=False),
):
    """
    Send a message to the AI agent.
    - If conversation_id is null, a new conversation is created.
    - If conversation_id is provided, the conversation is continued.
    """
    try:
        result = await chat_with_langchain(
            body.prompt,
            current_user,
            conversation_id=body.conversation_id,
            debug=debug,
        )
        return ChatResponse(
            reply=result["reply"],
            conversation_id=result["conversation_id"],
        )
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Conversations ────────────────────────────────────────────────


@router.get("/conversations", response_model=list[ConversationListItem])
async def list_conversations(current_user: CurrentUser):
    """List all conversations for the current user (sidebar data)."""
    conversations = await chat_repo.list_conversations(current_user["user_id"])
    return [ConversationListItem(**c) for c in conversations]


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageItem],
    )
async def get_conversation_messages(
    conversation_id: str,
    current_user: CurrentUser,
    ):
    """Load all messages for a conversation. Returns empty list if not found/not owned."""
    messages = await chat_repo.get_messages(conversation_id, current_user["user_id"])
    return [MessageItem(**m) for m in messages]


@router.put("/conversations/{conversation_id}", status_code=200)
async def rename_conversation(
    conversation_id: str,
    body: UpdateTitleRequest,
    current_user: CurrentUser,
):
    """Rename a conversation."""
    updated = await chat_repo.update_title(
        conversation_id, current_user["user_id"], body.title
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"success": True}


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    current_user: CurrentUser,
):
    """Soft-delete a conversation."""
    deleted = await chat_repo.delete_conversation(
        conversation_id, current_user["user_id"]
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found.")
