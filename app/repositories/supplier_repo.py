from uuid import uuid4
from typing import Optional
import asyncpg

from app.dto.supplier import (
    SupplierCreate,
    SupplierUpdate,
    SupplierRead,
)

# Supplier CRUD
async def create_supplier(
    conn: asyncpg.Connection, data: SupplierCreate, created_by: Optional[str] = None
) -> SupplierRead:
    row = await conn.fetchrow(
        """
        INSERT INTO suppliers (supplier_id, supplier_name, contact_email, contact_phone, address, status, created_by, updated_by)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $7)
        RETURNING supplier_id, supplier_name, contact_email, contact_phone, address, status,
                  created_at, updated_at, created_by, updated_by
        """,
        str(uuid4()), data.supplier_name, data.contact_email, data.contact_phone,
        data.address, data.status, created_by,
    )
    return SupplierRead(**dict(row))


async def get_supplier(conn: asyncpg.Connection, supplier_id: str, filter_supplier_id: Optional[str] = None) -> Optional[SupplierRead]:
    query = """
        SELECT supplier_id, supplier_name, contact_email, contact_phone, address, status,
               created_at, updated_at, created_by, updated_by
        FROM suppliers
        WHERE supplier_id = $1 AND deleted = FALSE
    """
    params = [supplier_id]
    if filter_supplier_id:
        query += " AND supplier_id = $2"
        params.append(filter_supplier_id)
        
    row = await conn.fetchrow(query, *params)
    if not row:
        return None
    return SupplierRead(**dict(row))


async def list_suppliers(
    conn: asyncpg.Connection, offset: int = 0, limit: int = 100, supplier_id: Optional[str] = None
) -> list[SupplierRead]:
    query = """
        SELECT supplier_id, supplier_name, contact_email, contact_phone, address, status,
               created_at, updated_at, created_by, updated_by
        FROM suppliers
        WHERE deleted = FALSE
    """
    params = [limit, offset]
    if supplier_id:
        query += " AND supplier_id = $3"
        params.append(supplier_id)
        
    query += " ORDER BY supplier_name LIMIT $1 OFFSET $2"
    
    rows = await conn.fetch(query, *params)
    return [SupplierRead(**dict(r)) for r in rows]


async def update_supplier(
    conn: asyncpg.Connection, supplier_id: str, data: SupplierUpdate, updated_by: Optional[str] = None, filter_supplier_id: Optional[str] = None
) -> Optional[SupplierRead]:
    query = """
        UPDATE suppliers
        SET
            supplier_name = COALESCE($1, supplier_name),
            contact_email = COALESCE($2, contact_email),
            contact_phone = COALESCE($3, contact_phone),
            address       = COALESCE($4, address),
            status        = COALESCE($5, status),
            updated_by    = $6,
            updated_at    = CURRENT_TIMESTAMP
        WHERE supplier_id = $7 AND deleted = FALSE
    """
    params = [
        data.supplier_name, data.contact_email, data.contact_phone,
        data.address, data.status, updated_by, supplier_id
    ]
    if filter_supplier_id:
        query = query.replace("WHERE supplier_id = $7", "WHERE supplier_id = $7 AND supplier_id = $8")
        params.append(filter_supplier_id)
        
    query += " RETURNING supplier_id, supplier_name, contact_email, contact_phone, address, status, created_at, updated_at, created_by, updated_by"
    
    row = await conn.fetchrow(query, *params)
    return SupplierRead(**dict(row)) if row else None


async def delete_supplier(
    conn: asyncpg.Connection, supplier_id: str, deleted_by: Optional[str] = None, filter_supplier_id: Optional[str] = None
) -> bool:
    query = """
        UPDATE suppliers
        SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
        WHERE supplier_id = $1 AND deleted = FALSE
    """
    params = [supplier_id, deleted_by]
    if filter_supplier_id:
        query += " AND supplier_id = $3"
        params.append(filter_supplier_id)
        
    result = await conn.execute(query, *params)
    return result == "UPDATE 1"

