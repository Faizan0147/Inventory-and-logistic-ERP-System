from fastapi import HTTPException
import asyncpg

from app.dto.supplier import SupplierCreate, SupplierUpdate, SupplierRead
from app.repositories import supplier_repo


async def create_supplier(
    conn: asyncpg.Connection, 
    body: SupplierCreate, 
    current_user: dict) -> SupplierRead:
    return await supplier_repo.create_supplier(
        conn, body, created_by=current_user["user_id"])


async def list_suppliers(
    conn: asyncpg.Connection, offset: int, limit: int) -> list[SupplierRead]:
    return await supplier_repo.list_suppliers(conn, offset, limit)


async def get_supplier(
    conn: asyncpg.Connection, supplier_id: str) -> SupplierRead:
    supplier = await supplier_repo.get_supplier(conn, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


async def update_supplier(
    conn: asyncpg.Connection, supplier_id: str, body: SupplierUpdate, current_user: dict
) -> SupplierRead:
    supplier = await supplier_repo.update_supplier(conn, supplier_id, body, updated_by=current_user["user_id"])
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


async def delete_supplier(conn: asyncpg.Connection, supplier_id: str, current_user: dict) -> None:
    deleted = await supplier_repo.delete_supplier(conn, supplier_id, deleted_by=current_user["user_id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Supplier not found")
