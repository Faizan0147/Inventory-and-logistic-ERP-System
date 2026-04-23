from fastapi import HTTPException
import asyncpg

from app.dto.inventory import InventoryCreate, InventoryRead, InventoryUpdate
from app.repositories import inventory_repo


async def create_inventory(
    conn: asyncpg.Connection,
    body: InventoryCreate,
    current_user: dict,
) -> InventoryRead:
    return await inventory_repo.create_inventory(
        conn, body, created_by=current_user["user_id"]
    )


async def get_inventory(
    conn: asyncpg.Connection, inventory_id: str, current_user: dict
) -> InventoryRead:
    user_id = current_user["user_id"] if current_user["role"] == "SUPPLIER" else None
    inventory = await inventory_repo.get_inventory(conn, inventory_id, user_id=user_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory


async def list_inventory(
    conn: asyncpg.Connection, offset: int, limit: int, current_user: dict
) -> list[InventoryRead]:
    user_id = current_user["user_id"] if current_user["role"] == "SUPPLIER" else None
    return await inventory_repo.list_inventory(conn, offset, limit, user_id=user_id)


async def update_inventory(
    conn: asyncpg.Connection,
    inventory_id: str,
    body: InventoryUpdate,
    current_user: dict,
) -> InventoryRead:
    user_id = current_user["user_id"] if current_user["role"] == "SUPPLIER" else None
    inventory = await inventory_repo.update_inventory(
        conn, inventory_id, body, updated_by=current_user["user_id"], user_id=user_id
    )
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found or access denied")
    return inventory


async def delete_inventory(
    conn: asyncpg.Connection, inventory_id: str, current_user: dict
) -> None:
    user_id = current_user["user_id"] if current_user["role"] == "SUPPLIER" else None
    deleted = await inventory_repo.delete_inventory(
        conn, inventory_id, deleted_by=current_user["user_id"], user_id=user_id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Inventory not found or access denied")
