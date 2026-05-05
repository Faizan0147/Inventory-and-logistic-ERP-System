import logging
from fastapi import HTTPException
import asyncpg

from app.dto.inventory import InventoryCreate, InventoryRead, InventoryUpdate
from app.repositories import inventory_repo

logger = logging.getLogger(__name__)


def _get_current_user(current_user: dict) -> str | None:
    return current_user["user_id"] if current_user["role"] == "SUPPLIER" else None


async def create_inventory(
    conn: asyncpg.Connection,
    body: InventoryCreate,
    current_user: dict,
) -> InventoryRead:

    try:
        return await inventory_repo.create_inventory(
            conn,
            body,
            user_id=current_user["user_id"],
            created_by=current_user["user_id"],
        )

    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    except RuntimeError as e:
        logger.error(
            "create_inventory failed for user %s: %s", current_user["user_id"], e
        )
        raise HTTPException(status_code=500, detail=str(e))


async def get_inventory(
    conn: asyncpg.Connection,
    inventory_id: str,
    current_user: dict,
) -> InventoryRead:

    try:
        inventory = await inventory_repo.get_inventory(
            conn, inventory_id, user_id=_get_current_user(current_user)
        )

    except RuntimeError as e:
        logger.error(
            "get_inventory(%s) failed for user %s: %s",
            inventory_id,
            current_user["user_id"],
            e,
        )
        raise HTTPException(status_code=500, detail=str(e))

    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory


async def list_inventory(
    conn: asyncpg.Connection,
    offset: int,
    limit: int,
    current_user: dict,
) -> list[InventoryRead]:

    try:
        return await inventory_repo.list_inventory(
            conn, offset, limit, user_id=_get_current_user(current_user)
        )

    except RuntimeError as e:
        logger.error(
            "list_inventory failed for user %s: %s", current_user["user_id"], e
        )
        raise HTTPException(status_code=500, detail=str(e))


async def update_inventory(
    conn: asyncpg.Connection,
    inventory_id: str,
    body: InventoryUpdate,
    current_user: dict,
) -> InventoryRead:

    try:
        inventory = await inventory_repo.update_inventory(
            conn,
            inventory_id,
            body,
            updated_by=current_user["user_id"],
            user_id=_get_current_user(current_user),
        )

    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    except RuntimeError as e:
        logger.error(
            "update_inventory(%s) failed for user %s: %s",
            inventory_id,
            current_user["user_id"],
            e,
        )
        raise HTTPException(status_code=500, detail=str(e))

    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory


async def delete_inventory(
    conn: asyncpg.Connection,
    inventory_id: str,
    current_user: dict,
) -> dict:

    try:
        deleted = await inventory_repo.delete_inventory(
            conn,
            inventory_id,
            deleted_by=current_user["user_id"],
            user_id=_get_current_user(current_user),
        )

    except RuntimeError as e:
        logger.error(
            "delete_inventory(%s) failed for user %s: %s",
            inventory_id,
            current_user["user_id"],
            e,
        )
        raise HTTPException(status_code=500, detail=str(e))

    if not deleted:
        raise HTTPException(status_code=404, detail="Inventory not found")

    return {"message": "Inventory deleted successfully"}
