import logging

from fastapi import HTTPException
import asyncpg

from app.utils.security import verify_password, create_access_token
from app.utils.email import send_credentials_email
from app.dto.auth import (
    RegistrationRequestCreate,
    RegistrationRequestRead,
    LoginRequest,
    TokenResponse,
    AuthUser,
)
from app.repositories import auth_repo, users_repo

logger = logging.getLogger(__name__)


async def register(
    conn: asyncpg.Connection, body: RegistrationRequestCreate
) -> RegistrationRequestRead:

    try:
        result = await auth_repo.create_registration_request(conn, body)
        return result

    except asyncpg.UniqueViolationError:
        raise HTTPException(
            status_code=409,
            detail="A registration request for this email already exists",
        )

    except asyncpg.PostgresError as exc:
        raise HTTPException(
            status_code=500, detail="DB error: Failed to submit registration request"
        )


async def login(conn: asyncpg.Connection, body: LoginRequest) -> TokenResponse:

    try:
        user = await users_repo.get_user_by_email(conn, body.email)

    except asyncpg.PostgresError as exc:
        raise HTTPException(
            status_code=500, detail="DB error: Login failed due to a server error"
        )

    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    try:
        token = create_access_token(
            data={
                "sub": user["user_id"],
                "role": user["role"],
            }
        )

    except Exception as exc:
        logger.error(
            "Token creation failed for email=%s: %s", body.email, exc, exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Login failed due to a server error"
        )

    return TokenResponse(
        access_token=token,
        user=AuthUser(
            user_id=str(user["user_id"]),
            name=user["name"],
            email=user["email"],
            role=user["role"],
        ),
    )
