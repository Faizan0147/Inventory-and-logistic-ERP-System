from fastapi import HTTPException
import asyncpg

from app.dto.poi import POItemCreate, POItemRead, POItemUpdate
from app.repositories import poi_repo


async def create_po_item(
    conn: asyncpg.Connection,
    body: POItemCreate,
    current_user: dict,
) -> POItemRead:
    return await poi_repo.create_po_item(
        conn, body, created_by=current_user["user_id"]
    )


async def list_po_items(
    conn: asyncpg.Connection, po_id: str, current_user: dict
) -> list[POItemRead]:
    user_id = current_user["user_id"] if current_user["role"] == "SUPPLIER" else None
    return await poi_repo.list_po_items(conn, po_id, user_id=user_id)


async def get_po_item(
    conn: asyncpg.Connection, po_item_id: str, current_user: dict
) -> POItemRead:
    user_id = current_user["user_id"] if current_user["role"] == "SUPPLIER" else None
    item = await poi_repo.get_po_item(conn, po_item_id, user_id=user_id)
    if not item:
        raise HTTPException(status_code=404, detail="PO item not found")
    return item


async def update_po_item(
    conn: asyncpg.Connection, po_item_id: str, body: POItemUpdate, current_user: dict
) -> POItemRead:
    user_id = current_user["user_id"] if current_user["role"] == "SUPPLIER" else None
    item = await poi_repo.update_po_item(
        conn, po_item_id, body, updated_by=current_user["user_id"], user_id=user_id
    )
    if not item:
        raise HTTPException(status_code=404, detail="PO item not found or access denied")
    return item


async def delete_po_item(
    conn: asyncpg.Connection, po_item_id: str, current_user: dict
) -> None:
    user_id = current_user["user_id"] if current_user["role"] == "SUPPLIER" else None
    deleted = await poi_repo.delete_po_item(
        conn, po_item_id, deleted_by=current_user["user_id"], user_id=user_id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="PO item not found or access denied")
