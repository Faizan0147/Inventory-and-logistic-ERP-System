import logging
from fastapi import HTTPException
import asyncpg

from app.dto.poi import POItemCreate, POItemRead, POItemUpdate
from app.repositories import poi_repo

logger = logging.getLogger(__name__)


def _get_current_user(current_user: dict) -> str | None:
    """Return user_id for SUPPLIER (scoped access), None for ADMIN (full access)."""
    return current_user["user_id"] if current_user["role"] == "SUPPLIER" else None


async def create_po_item(
    conn: asyncpg.Connection,
    body: POItemCreate,
    current_user: dict,
) -> POItemRead:
    try:
        return await poi_repo.create_po_item(
            conn, body, user_id=current_user["user_id"], created_by=current_user["user_id"]
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except RuntimeError as e:
        logger.error("create_po_item failed for user %s: %s", current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))


async def list_po_items(
    conn: asyncpg.Connection, 
    po_id: str, 
    current_user: dict
) -> list[POItemRead]:
    try:
        return await poi_repo.list_po_items(
            conn, po_id, user_id=_get_current_user(current_user)
        )
    except RuntimeError as e:
        logger.error("list_po_items(%s) failed for user %s: %s", po_id, current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))


async def get_po_item(
    conn: asyncpg.Connection, 
    po_item_id: str, 
    current_user: dict
) -> POItemRead:
    try:
        item = await poi_repo.get_po_item(
            conn, po_item_id, user_id=_get_current_user(current_user)
        )
    except RuntimeError as e:
        logger.error("get_po_item(%s) failed for user %s: %s", po_item_id, current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))

    if not item:
        raise HTTPException(status_code=404, detail="PO item not found")
    return item


async def update_po_item(
    conn: asyncpg.Connection, 
    po_item_id: str, 
    body: POItemUpdate, 
    current_user: dict
) -> POItemRead:
    try:
        item = await poi_repo.update_po_item(
            conn, po_item_id, body, 
            updated_by=current_user["user_id"], 
            user_id=_get_current_user(current_user)
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except RuntimeError as e:
        logger.error("update_po_item(%s) failed for user %s: %s", po_item_id, current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))

    if not item:
        raise HTTPException(status_code=404, detail="PO item not found")
    return item


async def delete_po_item(
    conn: asyncpg.Connection, 
    po_item_id: str, 
    current_user: dict
) -> dict:
    try:
        deleted = await poi_repo.delete_po_item(
            conn, po_item_id, 
            deleted_by=current_user["user_id"], 
            user_id=_get_current_user(current_user)
        )
    except RuntimeError as e:
        logger.error("delete_po_item(%s) failed for user %s: %s", po_item_id, current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))

    if not deleted:
        raise HTTPException(status_code=404, detail="PO item not found")
    
    return {"message": "Purchase order item deleted successfully"}
