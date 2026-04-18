from fastapi import HTTPException
import asyncpg

from app.dto.purchase_order import (
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderRead,
)
from app.repositories import purchase_order_repo


async def create_purchase_order(
    conn: asyncpg.Connection,
    body: PurchaseOrderCreate,
    current_user: dict) -> PurchaseOrderRead:
    return await purchase_order_repo.create_purchase_order(
        conn, body, created_by=current_user["user_id"])


async def list_purchase_orders(
    conn: asyncpg.Connection, offset: int, limit: int) -> list[PurchaseOrderRead]:
    return await purchase_order_repo.list_purchase_orders(conn, offset, limit)


async def get_purchase_order(
    conn: asyncpg.Connection, po_id: str) -> PurchaseOrderRead:
    po = await purchase_order_repo.get_purchase_order(conn, po_id)
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return po


async def update_purchase_order(
    conn: asyncpg.Connection, po_id: str, body: PurchaseOrderUpdate, current_user: dict
) -> PurchaseOrderRead:
    po = await purchase_order_repo.update_purchase_order(conn, po_id, body, updated_by=current_user["user_id"])
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return po


async def delete_purchase_order(
    conn: asyncpg.Connection, po_id: str, current_user: dict) -> None:
    deleted = await purchase_order_repo.delete_purchase_order(conn, po_id, deleted_by=current_user["user_id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Purchase order not found")