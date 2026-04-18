from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)

class ChatResponse(BaseModel):
    reply: str

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
