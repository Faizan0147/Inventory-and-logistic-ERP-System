import logging
import secrets
from fastapi import HTTPException
import asyncpg
from asyncpg.exceptions import UniqueViolationError
from app.utils.security import hash_password
from app.utils.email import send_credentials_email
from app.dto.auth import ApproveRequestBody, RegistrationRequestRead
from app.dto.users import UserCreate, UserRead
from app.repositories import auth_repo, users_repo

logger = logging.getLogger(__name__)


async def list_pending_requests(conn: asyncpg.Connection) -> list[RegistrationRequestRead]:
    try:
        results = await auth_repo.list_pending_requests(conn)
        return results

    except asyncpg.PostgresError as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch registration requests")


async def approve_request(
    conn: asyncpg.Connection, 
    request_id: str, body: 
    ApproveRequestBody, 
    current_user: dict
) -> UserRead:

    try:
        req = await auth_repo.get_request_by_id(conn, request_id)
        
    except asyncpg.PostgresError as exc:
        raise HTTPException(status_code=500, detail="DB error: Failed to fetch registration request")

    if not req:
        raise HTTPException(status_code=404, detail="Approve failed: Registration request not found")

    if req.status != "PENDING":
        raise HTTPException(status_code=400, detail="Request already processed")

    temp_password = secrets.token_urlsafe(12)
    hashed = hash_password(temp_password)

    try:
        existing_user = await users_repo.get_user_by_email(conn, req.email)

    except asyncpg.PostgresError as exc:
        raise HTTPException(status_code=500, detail="DB error: Failed to process approval")

    if existing_user:
        await auth_repo.update_request_status(
            conn, request_id, status="REJECTED", reviewed_by=current_user["user_id"]
        )
        raise HTTPException(status_code=409, detail=f"User with email {req.email} already exists")

    try:
        user = await users_repo.create_user(
            conn,
            data=UserCreate(
                name=req.name,
                email=req.email,
                password=temp_password,
                phone_number=req.phone,
                role=body.role,
            ),
            password_hash=hashed,
            created_by=current_user["user_id"],
        )

    except UniqueViolationError:
        raise HTTPException(status_code=409, detail=f"User with email {req.email} already exists")

    except asyncpg.PostgresError as exc:
        raise HTTPException(status_code=500, detail="Failed to create user account")

    try:
        await auth_repo.update_request_status(
            conn, request_id, status="APPROVED", reviewed_by=current_user["user_id"]
        )
    except asyncpg.PostgresError as exc:
        raise HTTPException(status_code=500, detail="DB error: User created but failed to update request status")

    try:
        await send_credentials_email(req.email, req.name, temp_password)

    except Exception as exc:
        logger.error("Failed to send credentials email to email=%s: %s", req.email, exc, exc_info=True)

    return user


async def reject_request(
    conn: asyncpg.Connection, request_id: str, current_user: dict
) -> None:

    try:
        req = await auth_repo.get_request_by_id(conn, request_id)
    except asyncpg.PostgresError as exc:
        raise HTTPException(status_code=500, detail="DB error: Failed to fetch registration request")

    if not req:
        raise HTTPException(status_code=404, detail="Registration request not found")

    if req.status != "PENDING":
        raise HTTPException(status_code=400, detail="Request already processed")

    try:
        await auth_repo.update_request_status(
            conn, request_id, status="REJECTED", reviewed_by=current_user["user_id"]
        )

        logger.info("Request rejected: request_id=%s by admin=%s", request_id, current_user["user_id"])

    except asyncpg.PostgresError as exc:
        logger.error("DB error rejecting request_id=%s: %s", request_id, exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to reject registration request")
