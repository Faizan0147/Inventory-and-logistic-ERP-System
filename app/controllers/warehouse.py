import logging
from fastapi import HTTPException
import asyncpg

from app.dto.warehouse import WarehouseCreate, WarehouseRead, WarehouseUpdate
from app.repositories import warehouse_repo

logger = logging.getLogger(__name__)


def _get_current_user(current_user: dict) -> str | None:
    """Return user_id for SUPPLIER (scoped access), None for ADMIN (full access)."""
    return current_user["user_id"] if current_user["role"] == "SUPPLIER" else None


async def create_warehouse(
    conn: asyncpg.Connection,
    body: WarehouseCreate,
    current_user: dict,
) -> WarehouseRead:
    try:
        return await warehouse_repo.create_warehouse(
            conn, body, user_id=current_user["user_id"], created_by=current_user["user_id"]
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except RuntimeError as e:
        logger.error("create_warehouse failed for user %s: %s", current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))


async def get_warehouse(
    conn: asyncpg.Connection, 
    warehouse_id: str,
    current_user: dict
) -> WarehouseRead:
    try:
        warehouse = await warehouse_repo.get_warehouse(
            conn, warehouse_id, user_id=_get_current_user(current_user)
        )
    except RuntimeError as e:
        logger.error("get_warehouse(%s) failed for user %s: %s", warehouse_id, current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))

    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse


async def list_warehouses(
    conn: asyncpg.Connection, 
    offset: int, 
    limit: int,
    current_user: dict
) -> list[WarehouseRead]:
    try:
        return await warehouse_repo.list_warehouses(
            conn, offset, limit, user_id=_get_current_user(current_user)
        )
    except RuntimeError as e:
        logger.error("list_warehouses failed for user %s: %s", current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))


async def update_warehouse(
    conn: asyncpg.Connection,
    warehouse_id: str,
    body: WarehouseUpdate,
    current_user: dict,
) -> WarehouseRead:
    try:
        warehouse = await warehouse_repo.update_warehouse(
            conn, warehouse_id, body, 
            updated_by=current_user["user_id"],
            user_id=_get_current_user(current_user)
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except RuntimeError as e:
        logger.error("update_warehouse(%s) failed for user %s: %s", warehouse_id, current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))

    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse


async def delete_warehouse(
    conn: asyncpg.Connection, 
    warehouse_id: str, 
    current_user: dict
) -> dict:
    try:
        deleted = await warehouse_repo.delete_warehouse(
            conn, warehouse_id, 
            deleted_by=current_user["user_id"],
            user_id=_get_current_user(current_user)
        )
    except RuntimeError as e:
        logger.error("delete_warehouse(%s) failed for user %s: %s", warehouse_id, current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))

    if not deleted:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    return {"message": "Warehouse deleted successfully"}