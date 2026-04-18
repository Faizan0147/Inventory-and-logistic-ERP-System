from typing import Annotated

from fastapi import APIRouter, Depends, status, Response
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

Conn = Annotated[asyncpg.Connection, Depends(get_connection)]


@router.post("/register", response_model=RegistrationRequestRead, status_code=status.HTTP_201_CREATED)
async def register(body: RegistrationRequestCreate, conn: Conn):
    return await auth_controller.register(conn, body)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, conn: Conn, response: Response):
    # Return token in JSON and set a secure HttpOnly cookie so the browser
    # automatically sends it on subsequent requests.
    token_resp = await auth_controller.login(conn, body)
    response.set_cookie(
        key="access_token",
        value=token_resp.access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )
    return token_resp
