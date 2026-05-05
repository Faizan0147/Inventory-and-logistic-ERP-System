import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg

from app.database import get_connection
from app.utils.dependencies import require_role
from app.dto.auth import RegistrationRequestRead
from app.dto.users import UserRead
from app.controllers import admin as admin_controller

router = APIRouter()
logger = logging.getLogger(__name__)

Conn = Annotated[asyncpg.Connection, Depends(get_connection)]
SuperAdmin = Annotated[dict, Depends(require_role("SUPERADMIN"))]

@router.get("/registration-requests", response_model=list[RegistrationRequestRead])
async def list_requests(current_user: SuperAdmin, conn: Conn):

    try:
        return await admin_controller.list_pending_requests(conn)
    
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/registration-requests/{request_id}/approve", response_model=UserRead)
async def approve_request(
    request_id: str, current_user: SuperAdmin, conn: Conn
):
    try:
        return await admin_controller.approve_request(conn, request_id, current_user)

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/registration-requests/{request_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
async def reject_request(request_id: str, current_user: SuperAdmin, conn: Conn):

    try:
        await admin_controller.reject_request(conn, request_id, current_user)

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
