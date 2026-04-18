from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.controllers.chat import chat_with_mcp
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
        result = await chat_with_mcp(body.prompt, current_user, debug=debug)
        return ChatResponse(reply=result["reply"])
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
