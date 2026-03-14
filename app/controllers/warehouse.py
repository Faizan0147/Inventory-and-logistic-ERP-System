from fastapi import HTTPException
import asyncpg

from app.dto.warehouse import WarehouseCreate, WarehouseRead, WarehouseUpdate
from app.repositories import warehouse_repo


async def create_warehouse(
    conn: asyncpg.Connection,
    body: WarehouseCreate,
    current_user: dict,
) -> WarehouseRead:
    return await warehouse_repo.create_warehouse(
        conn, body, created_by=current_user["user_id"]
    )


async def get_warehouse(
    conn: asyncpg.Connection, warehouse_id: str
) -> WarehouseRead:
    warehouse = await warehouse_repo.get_warehouse(conn, warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse


async def list_warehouses(
    conn: asyncpg.Connection, offset: int, limit: int
) -> list[WarehouseRead]:
    return await warehouse_repo.list_warehouses(conn, offset, limit)


async def update_warehouse(
    conn: asyncpg.Connection,
    warehouse_id: str,
    body: WarehouseUpdate,
    current_user: dict,
) -> WarehouseRead:
    warehouse = await warehouse_repo.update_warehouse(
        conn, warehouse_id, body, updated_by=current_user["user_id"]
    )
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse


async def delete_warehouse(
    conn: asyncpg.Connection, warehouse_id: str, current_user: dict
) -> None:
    deleted = await warehouse_repo.delete_warehouse(
        conn, warehouse_id, deleted_by=current_user["user_id"]
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Warehouse not found")