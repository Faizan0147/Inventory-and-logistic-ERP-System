from fastapi import HTTPException
import asyncpg

from app.dto.supplier import SupplierCreate, SupplierUpdate, SupplierRead
from app.repositories import supplier_repo


async def create_supplier(
    conn: asyncpg.Connection, 
    body: SupplierCreate, 
    current_user: dict) -> SupplierRead:
    # Only SUPERADMIN can create new suppliers
    if current_user["role"] != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Only admins can create suppliers")
        
    return await supplier_repo.create_supplier(
        conn, body, created_by=current_user["user_id"])


async def list_suppliers(
    conn: asyncpg.Connection, offset: int, limit: int, current_user: dict) -> list[SupplierRead]:
    supplier_id = current_user["supplier_id"] if current_user["role"] == "SUPPLIER" else None
    return await supplier_repo.list_suppliers(conn, offset, limit, supplier_id=supplier_id)


async def get_supplier(
    conn: asyncpg.Connection, supplier_id: str, current_user: dict) -> SupplierRead:
    filter_supplier_id = current_user["supplier_id"] if current_user["role"] == "SUPPLIER" else None
    supplier = await supplier_repo.get_supplier(conn, supplier_id, filter_supplier_id=filter_supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found or access denied")
    return supplier


async def update_supplier(
    conn: asyncpg.Connection, supplier_id: str, body: SupplierUpdate, current_user: dict
) -> SupplierRead:
    filter_supplier_id = current_user["supplier_id"] if current_user["role"] == "SUPPLIER" else None
    supplier = await supplier_repo.update_supplier(conn, supplier_id, body, updated_by=current_user["user_id"], filter_supplier_id=filter_supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found or access denied")
    return supplier


async def delete_supplier(conn: asyncpg.Connection, supplier_id: str, current_user: dict) -> None:
    # Only SUPERADMIN can delete suppliers
    if current_user["role"] != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Only admins can delete suppliers")

    deleted = await supplier_repo.delete_supplier(conn, supplier_id, deleted_by=current_user["user_id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Supplier not found")

