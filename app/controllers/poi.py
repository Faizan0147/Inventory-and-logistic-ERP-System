from fastapi import HTTPException
import asyncpg

from app.dto.poi import (
    POItemCreate, POItemRead, POItemUpdate
)
from app.repositories import poi_repo

async def create_po_item(
    conn: asyncpg.Connection,
    body: POItemCreate,
    current_user: dict) -> POItemRead:
    return await poi_repo.create_po_item(
        conn, body, created_by=current_user["user_id"])


async def list_po_items(
    conn: asyncpg.Connection, po_id: str) -> list[POItemRead]:
    return await poi_repo.list_po_items(conn, po_id)


async def get_po_item(
    conn: asyncpg.Connection, po_item_id: str) -> POItemRead:
    item = await poi_repo.get_po_item(conn, po_item_id)
    if not item:
        raise HTTPException(status_code=404, detail="PO item not found")
    return item


async def update_po_item(
    conn: asyncpg.Connection, po_item_id: str, body: POItemUpdate, current_user: dict
) -> POItemRead:
    item = await poi_repo.update_po_item(conn, po_item_id, body, updated_by=current_user["user_id"])
    if not item:
        raise HTTPException(status_code=404, detail="PO item not found")
    return item


async def delete_po_item(
    conn: asyncpg.Connection, po_item_id: str, current_user: dict) -> None:
    deleted = await poi_repo.delete_po_item(conn, po_item_id, deleted_by=current_user["user_id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="PO item not found")