import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
import asyncpg

from app.database import get_connection
from app.dto.auth import (
    RegistrationRequestCreate,
    RegistrationRequestRead,
    LoginRequest,
    TokenResponse,
)
from app.controllers import auth as auth_controller

router = APIRouter()
logger = logging.getLogger(__name__)

Conn = Annotated[asyncpg.Connection, Depends(get_connection)]


@router.post(
    "/register",
    response_model=RegistrationRequestRead,
    status_code=status.HTTP_201_CREATED,
)
async def register(body: RegistrationRequestCreate, conn: Conn, request: Request):
    try:
        return await auth_controller.register(conn, body)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            "Unexpected error in POST /register email=%s: %s",
            body.email,
            exc,
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, conn: Conn, request: Request):

    try:
        return await auth_controller.login(conn, body)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            "Unexpected error in POST /login email=%s: %s",
            body.email,
            exc,
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
