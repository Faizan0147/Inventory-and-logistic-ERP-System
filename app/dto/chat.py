from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


# ── Chat Message Request / Response ──────────────────────────────

class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = Field(
        default=None,
        description="Pass an existing conversation_id to continue a chat. "
                    "Leave null to start a new conversation.",
    )


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str


# ── Conversation Management ──────────────────────────────────────

class ConversationListItem(BaseModel):
    conversation_id: str
    title: str
    message_count: int
    created_at: datetime
    updated_at: datetime


class MessageItem(BaseModel):
    message_id: str
    role: str
    content: str
    created_at: datetime


class UpdateTitleRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)


# ── Debug Models (unchanged) ────────────────────────────────────

class ChatToolCall(BaseModel):
    name: str
    arguments: dict
    result: str


class ChatDebugResponse(BaseModel):
    model: str
    final_reply: str
    tool_calls: list[ChatToolCall]


class ChatMode(BaseModel):
    mode: Literal["answer", "debug"] = "answer"
