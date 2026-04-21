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
    # If the user is a SUPPLIER, ensure they are creating a PO for themselves
    if current_user["role"] == "SUPPLIER" and body.supplier_id != current_user["supplier_id"]:
         raise HTTPException(status_code=403, detail="Suppliers can only create purchase orders for themselves")
         
    return await purchase_order_repo.create_purchase_order(
        conn, body, created_by=current_user["user_id"])


async def list_purchase_orders(
    conn: asyncpg.Connection, offset: int, limit: int, current_user: dict) -> list[PurchaseOrderRead]:
    supplier_id = current_user["supplier_id"] if current_user["role"] == "SUPPLIER" else None
    return await purchase_order_repo.list_purchase_orders(conn, offset, limit, supplier_id=supplier_id)


async def get_purchase_order(
    conn: asyncpg.Connection, po_id: str, current_user: dict) -> PurchaseOrderRead:
    supplier_id = current_user["supplier_id"] if current_user["role"] == "SUPPLIER" else None
    po = await purchase_order_repo.get_purchase_order(conn, po_id, supplier_id=supplier_id)
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return po


async def update_purchase_order(
    conn: asyncpg.Connection, po_id: str, body: PurchaseOrderUpdate, current_user: dict
) -> PurchaseOrderRead:
    supplier_id = current_user["supplier_id"] if current_user["role"] == "SUPPLIER" else None
    
    # If a supplier tries to update and changes the supplier_id, block it
    if current_user["role"] == "SUPPLIER" and body.supplier_id and body.supplier_id != current_user["supplier_id"]:
        raise HTTPException(status_code=403, detail="Cannot change supplier assignment")
        
    po = await purchase_order_repo.update_purchase_order(conn, po_id, body, updated_by=current_user["user_id"], supplier_id=supplier_id)
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found or access denied")
    return po


async def delete_purchase_order(
    conn: asyncpg.Connection, po_id: str, current_user: dict) -> None:
    supplier_id = current_user["supplier_id"] if current_user["role"] == "SUPPLIER" else None
    deleted = await purchase_order_repo.delete_purchase_order(conn, po_id, deleted_by=current_user["user_id"], supplier_id=supplier_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Purchase order not found or access denied")