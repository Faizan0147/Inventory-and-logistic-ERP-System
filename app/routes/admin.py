from typing import Annotated

from fastapi import APIRouter, Depends, status
import asyncpg

from app.database import get_connection
from app.utils.dependencies import require_role
from app.dto.auth import ApproveRequestBody, RegistrationRequestRead
from app.dto.users import UserRead
from app.controllers import admin as admin_controller

router = APIRouter()

Conn = Annotated[asyncpg.Connection, Depends(get_connection)]
SuperAdmin = Annotated[dict, Depends(require_role("SUPERADMIN"))]


@router.get("/registration-requests", response_model=list[RegistrationRequestRead])
async def list_requests(current_user: SuperAdmin, conn: Conn):
    return await admin_controller.list_pending_requests(conn)


@router.post("/registration-requests/{request_id}/approve", response_model=UserRead)
async def approve_request(request_id: str, body: ApproveRequestBody, current_user: SuperAdmin, conn: Conn):
    return await admin_controller.approve_request(conn, request_id, body, current_user)


@router.post("/registration-requests/{request_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
async def reject_request(request_id: str, current_user: SuperAdmin, conn: Conn):
    await admin_controller.reject_request(conn, request_id, current_user)
