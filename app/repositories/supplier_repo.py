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


async def get_supplier(conn: asyncpg.Connection, supplier_id: str) -> Optional[SupplierRead]:
    row = await conn.fetchrow(
        """
        SELECT supplier_id, supplier_name, contact_email, contact_phone, address, status,
               created_at, updated_at, created_by, updated_by
        FROM suppliers
        WHERE supplier_id = $1 AND deleted = FALSE
        """,
        supplier_id,
    )
    if not row:
        return None
    return SupplierRead(**dict(row))


async def list_suppliers(
    conn: asyncpg.Connection, offset: int = 0, limit: int = 100
) -> list[SupplierRead]:
    rows = await conn.fetch(
        """
        SELECT supplier_id, supplier_name, contact_email, contact_phone, address, status,
               created_at, updated_at, created_by, updated_by
        FROM suppliers
        WHERE deleted = FALSE
        ORDER BY supplier_name
        LIMIT $1 OFFSET $2
        """,
        limit, offset,
    )
    return [SupplierRead(**dict(r)) for r in rows]


async def update_supplier(
    conn: asyncpg.Connection, supplier_id: str, data: SupplierUpdate, updated_by: Optional[str] = None
) -> Optional[SupplierRead]:
    row = await conn.fetchrow(
        """
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
        RETURNING supplier_id, supplier_name, contact_email, contact_phone, address, status,
                  created_at, updated_at, created_by, updated_by
        """,
        data.supplier_name, data.contact_email, data.contact_phone,
        data.address, data.status, updated_by, supplier_id,
    )
    return SupplierRead(**dict(row)) if row else None


async def delete_supplier(
    conn: asyncpg.Connection, supplier_id: str, deleted_by: Optional[str] = None
) -> bool:
    result = await conn.execute(
        """
        UPDATE suppliers
        SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
        WHERE supplier_id = $1 AND deleted = FALSE
        """,
        supplier_id, deleted_by,
    )
    return result == "UPDATE 1"
