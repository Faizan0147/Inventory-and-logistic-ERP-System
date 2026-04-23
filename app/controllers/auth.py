from fastapi import HTTPException
import asyncpg

from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.email import send_credentials_email
from app.dto.auth import (
    RegistrationRequestCreate,
    RegistrationRequestRead,
    LoginRequest,
    TokenResponse,
    AuthUser
)
from app.repositories import auth_repo, users_repo


async def register(conn: asyncpg.Connection, body: RegistrationRequestCreate) -> RegistrationRequestRead:
    return await auth_repo.create_registration_request(conn, body)


async def login(conn: asyncpg.Connection, body: LoginRequest) -> TokenResponse:
    user = await users_repo.get_user_by_email(conn, body.email)
    print(body.email)
    print(body.password)
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    token = create_access_token(
        data={
            "sub": user["user_id"],
            "role": user["role"],
        }
    )
    return TokenResponse(
        access_token=token,
        user=AuthUser(
            user_id=str(user["user_id"]),
            name=user["name"],
            email=user["email"],
            role=user["role"],
            # supplier_id=user.get("supplier_id"),
        ),
    )
