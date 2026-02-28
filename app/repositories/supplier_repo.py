from uuid import UUID, uuid4
from typing import Optional
import asyncpg

from app.dto.supplier import (
    SupplierCreate,
    SupplierUpdate,
    SupplierRead,
    SupplierWithBankDetails,
)
from app.dto.supplierbankdetails import (
    SupplierBankDetailsCreate,
    SupplierBankDetailsRead,
)

# Supplier CRUD

async def create_supplier(conn: asyncpg.Connection, data: SupplierCreate) -> SupplierRead:
    row = await conn.fetchrow(
        """
        INSERT INTO supplier (supplier_id, name, contact_info, address)
        VALUES ($1, $2, $3, $4)
        RETURNING supplier_id, name, contact_info, address
        """,
        uuid4(), data.name, data.contact_info, data.address,
    )
    return SupplierRead(**dict(row))


async def get_supplier(conn: asyncpg.Connection, supplier_id: UUID) -> Optional[SupplierWithBankDetails]:
    row = await conn.fetchrow(
        "SELECT supplier_id, name, contact_info, address FROM supplier WHERE supplier_id = $1",
        supplier_id,
    )
    if not row:
        return None

    bank_rows = await conn.fetch(
        """
        SELECT bank_detail_id, supplier_id, bank_name, account_number, routing_number
        FROM supplier_bank_details
        WHERE supplier_id = $1
        """,
        supplier_id,
    )
    bank_details = [SupplierBankDetailsRead(**dict(r)) for r in bank_rows]
    return SupplierWithBankDetails(**dict(row), bank_details=bank_details)


async def list_suppliers(
    conn: asyncpg.Connection, offset: int = 0, limit: int = 100
) -> list[SupplierRead]:
    rows = await conn.fetch(
        "SELECT supplier_id, name, contact_info, address FROM supplier ORDER BY name LIMIT $1 OFFSET $2",
        limit, offset,
    )
    return [SupplierRead(**dict(r)) for r in rows]


async def update_supplier(
    conn: asyncpg.Connection, supplier_id: UUID, data: SupplierUpdate
) -> Optional[SupplierRead]:
    row = await conn.fetchrow(
        """
        UPDATE supplier
        SET
            name         = COALESCE($1, name),
            contact_info = COALESCE($2, contact_info),
            address      = COALESCE($3, address)
        WHERE supplier_id = $4
        RETURNING supplier_id, name, contact_info, address
        """,
        data.name, data.contact_info, data.address, supplier_id,
    )
    return SupplierRead(**dict(row)) if row else None


async def delete_supplier(conn: asyncpg.Connection, supplier_id: UUID) -> bool:
    result = await conn.execute("DELETE FROM supplier WHERE supplier_id = $1", supplier_id)
    return result == "DELETE 1"


# ─────────────────────────────────────────────
# Supplier Bank Details CRUD
# ─────────────────────────────────────────────

async def add_bank_details(
    conn: asyncpg.Connection, supplier_id: UUID, data: SupplierBankDetailsCreate
) -> SupplierBankDetailsRead:
    row = await conn.fetchrow(
        """
        INSERT INTO supplier_bank_details (bank_detail_id, supplier_id, bank_name, account_number, routing_number)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING bank_detail_id, supplier_id, bank_name, account_number, routing_number
        """,
        uuid4(), supplier_id, data.bank_name, data.account_number, data.routing_number,
    )
    return SupplierBankDetailsRead(**dict(row))


async def delete_bank_details(conn: asyncpg.Connection, bank_detail_id: UUID) -> bool:
    result = await conn.execute(
        "DELETE FROM supplier_bank_details WHERE bank_detail_id = $1", bank_detail_id
    )
    return result == "DELETE 1"
