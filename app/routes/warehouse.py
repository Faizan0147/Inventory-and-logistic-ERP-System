from typing import Annotated

from fastapi import APIRouter, Depends, status
import asyncpg

from app.database import get_connection
from app.utils.dependencies import get_current_user
from app.dto.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseRead
from app.controllers import warehouse as warehouse_controller

router = APIRouter()

Conn = Annotated[asyncpg.Connection, Depends(get_connection)]
CurrentUser = Annotated[dict, Depends(get_current_user)]


@router.post("/", response_model=WarehouseRead, status_code=status.HTTP_201_CREATED)
async def create_warehouse(body: WarehouseCreate, conn: Conn, current_user: CurrentUser):
    return await warehouse_controller.create_warehouse(conn, body, current_user)


@router.get("/", response_model=list[WarehouseRead])
async def list_warehouse(conn: Conn, current_user: CurrentUser, offset: int = 0, limit: int = 100):
    return await warehouse_controller.list_warehouses(conn, offset, limit, current_user)


@router.get("/{warehouse_id}", response_model=WarehouseRead)
async def get_warehouse(warehouse_id: str, conn: Conn, current_user: CurrentUser):
    return await warehouse_controller.get_warehouse(conn, warehouse_id, current_user)


@router.put("/{warehouse_id}", response_model=WarehouseRead)
async def update_warehouse(warehouse_id: str, body: WarehouseUpdate, conn: Conn, current_user: CurrentUser):
    return await warehouse_controller.update_warehouse(conn, warehouse_id, body, current_user)


@router.delete("/{warehouse_id}", status_code=200)
async def delete_warehouse(warehouse_id: str, conn: Conn, current_user: CurrentUser) -> dict:
    return await warehouse_controller.delete_warehouse(conn, warehouse_id, current_user)