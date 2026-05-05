from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.langchain_agent.chat import chat_with_langchain, clear_session
from app.dto.chat import ChatRequest, ChatResponse
from app.utils.dependencies import get_current_user

router = APIRouter()

CurrentUser = Annotated[dict, Depends(get_current_user)]


@router.post("/message", response_model=ChatResponse)
async def send_message(
    body: ChatRequest,
    current_user: CurrentUser,
    debug: bool = Query(default=False),
):
    try:
        result = await chat_with_langchain(
            body.prompt, current_user, session_id=body.session_id, debug=debug
        )
        return ChatResponse(reply=result["reply"])
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/session/{session_id}", status_code=204)
async def delete_session(session_id: str, current_user: CurrentUser):
    """Clear conversation history for a session."""
    clear_session(session_id)
