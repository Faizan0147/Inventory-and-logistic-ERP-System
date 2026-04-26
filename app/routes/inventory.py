from typing import Annotated

from fastapi import APIRouter, Depends, status
import asyncpg

from app.database import get_connection
from app.utils.dependencies import get_current_user
from app.dto.inventory import InventoryCreate, InventoryUpdate, InventoryRead
from app.controllers import inventory as inventory_controller

router = APIRouter()

Conn = Annotated[asyncpg.Connection, Depends(get_connection)]
CurrentUser = Annotated[dict, Depends(get_current_user)]


@router.post("/", response_model=InventoryRead, status_code=status.HTTP_201_CREATED)
async def create_inventory(body: InventoryCreate, conn: Conn, current_user: CurrentUser):
    return await inventory_controller.create_inventory(conn, body, current_user)


@router.get("/", response_model=list[InventoryRead])
async def list_inventory(conn: Conn, current_user: CurrentUser, offset: int = 0, limit: int = 100):
    return await inventory_controller.list_inventory(conn, offset, limit, current_user=current_user)


@router.get("/{inventory_id}", response_model=InventoryRead)
async def get_inventory(inventory_id: str, conn: Conn, current_user: CurrentUser):
    return await inventory_controller.get_inventory(conn, inventory_id, current_user=current_user)


@router.put("/{inventory_id}", response_model=InventoryRead)
async def update_inventory(inventory_id: str, body: InventoryUpdate, conn: Conn, current_user: CurrentUser):
    return await inventory_controller.update_inventory(conn, inventory_id, body, current_user)


@router.delete("/{inventory_id}", status_code=200)
async def delete_inventory(inventory_id: str, conn: Conn, current_user: CurrentUser) -> dict:
    return await inventory_controller.delete_inventory(conn, inventory_id, current_user)
