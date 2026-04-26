import logging
from fastapi import HTTPException
import asyncpg

from app.dto.purchase_order import (
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderRead,
)
from app.repositories import purchase_order_repo

logger = logging.getLogger(__name__)


def _get_current_user(current_user: dict) -> str | None:
    """Return user_id for SUPPLIER (scoped access), None for ADMIN (full access)."""
    return current_user["user_id"] if current_user["role"] == "SUPPLIER" else None


async def create_purchase_order(
    conn: asyncpg.Connection,
    body: PurchaseOrderCreate,
    current_user: dict,
) -> PurchaseOrderRead:
    try:
        return await purchase_order_repo.create_purchase_order(
            conn, body, user_id=current_user["user_id"], created_by=current_user["user_id"]
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except RuntimeError as e:
        logger.error("create_purchase_order failed for user %s: %s", current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))


async def get_purchase_order(
    conn: asyncpg.Connection, 
    po_id: str, 
    current_user: dict
) -> PurchaseOrderRead:
    try:
        po = await purchase_order_repo.get_purchase_order(
            conn, po_id, user_id=_get_current_user(current_user)
        )
    except RuntimeError as e:
        logger.error("get_purchase_order(%s) failed for user %s: %s", po_id, current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))

    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return po


async def list_purchase_orders(
    conn: asyncpg.Connection, 
    offset: int, 
    limit: int, 
    current_user: dict
) -> list[PurchaseOrderRead]:
    try:
        return await purchase_order_repo.list_purchase_orders(
            conn, offset, limit, user_id=_get_current_user(current_user)
        )
    except RuntimeError as e:
        logger.error("list_purchase_orders failed for user %s: %s", current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))


async def update_purchase_order(
    conn: asyncpg.Connection, 
    po_id: str, 
    body: PurchaseOrderUpdate, 
    current_user: dict
) -> PurchaseOrderRead:
    try:
        po = await purchase_order_repo.update_purchase_order(
            conn, po_id, body, 
            updated_by=current_user["user_id"], 
            user_id=_get_current_user(current_user)
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except RuntimeError as e:
        logger.error("update_purchase_order(%s) failed for user %s: %s", po_id, current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))

    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return po


async def delete_purchase_order(
    conn: asyncpg.Connection, 
    po_id: str, 
    current_user: dict
) -> dict:
    try:
        deleted = await purchase_order_repo.delete_purchase_order(
            conn, po_id, 
            deleted_by=current_user["user_id"], 
            user_id=_get_current_user(current_user)
        )
    except RuntimeError as e:
        logger.error("delete_purchase_order(%s) failed for user %s: %s", po_id, current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))

    if not deleted:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    return {"message": "Purchase order deleted successfully"}
