import secrets

from fastapi import HTTPException
import asyncpg
from asyncpg.exceptions import UniqueViolationError

from app.utils.security import hash_password
from app.utils.email import send_credentials_email
from app.dto.auth import ApproveRequestBody, RegistrationRequestRead
from app.dto.users import UserCreate, UserRead
from app.repositories import auth_repo, users_repo


async def list_pending_requests(conn: asyncpg.Connection) -> list[RegistrationRequestRead]:
    return await auth_repo.list_pending_requests(conn)


async def approve_request(
    conn: asyncpg.Connection, request_id: str, body: ApproveRequestBody, current_user: dict
) -> UserRead:
    req = await auth_repo.get_request_by_id(conn, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Registration request not found")
    if req.status != "PENDING":
        raise HTTPException(status_code=400, detail="Request already processed")

    temp_password = secrets.token_urlsafe(12)
    hashed = hash_password(temp_password)

    existing_user = await users_repo.get_user_by_email(conn, req.email)
    if existing_user:
        await auth_repo.update_request_status(
            conn, request_id, status="REJECTED", reviewed_by=current_user["user_id"]
        )
        raise HTTPException(
            status_code=409,
            detail=f"User with email {req.email} already exists",
        )

    try:
        user = await users_repo.create_user(
            conn,
            data=UserCreate(
                name=req.name,
                email=req.email,
                password=temp_password,
                phone_number=req.phone,
                role=body.role,
                supplier_id=None,
            ),
            password_hash=hashed,
            created_by=current_user["user_id"],
        )
    except UniqueViolationError:
        raise HTTPException(
            status_code=409,
            detail=f"User with email {req.email} already exists",
        )

    await auth_repo.update_request_status(
        conn, request_id, status="APPROVED", reviewed_by=current_user["user_id"]
    )

    await send_credentials_email(req.email, req.name, temp_password)

    return user


async def reject_request(
    conn: asyncpg.Connection, request_id: str, current_user: dict
) -> None:
    req = await auth_repo.get_request_by_id(conn, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Registration request not found")
    if req.status != "PENDING":
        raise HTTPException(status_code=400, detail="Request already processed")

    await auth_repo.update_request_status(
        conn, request_id, status="REJECTED", reviewed_by=current_user["user_id"]
    )
