from typing import Annotated, Union

from fastapi import APIRouter, Depends
import asyncpg

from app.database import get_connection
from app.utils.dependencies import get_current_user
from app.dto.dashboard import SuperAdminDashboard, SupplierDashboard
from app.controllers import dashboard as dashboard_controller

router = APIRouter()

Conn = Annotated[asyncpg.Connection, Depends(get_connection)]
CurrentUser = Annotated[dict, Depends(get_current_user)]


@router.get("/", response_model=Union[SuperAdminDashboard, SupplierDashboard])
async def get_dashboard(conn: Conn, current_user: CurrentUser):
    return await dashboard_controller.get_dashboard(conn, current_user)
