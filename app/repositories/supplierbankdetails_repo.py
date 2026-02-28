from uuid import UUID, uuid4
from typing import Optional
import asyncpg


from app.dto.supplier import (
    SupplierBankDetailsCreate,
    SupplierBankDetailsRead,
    SupplierWithBankDetails
)



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