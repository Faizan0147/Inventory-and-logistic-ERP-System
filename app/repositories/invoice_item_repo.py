from uuid import uuid4
from typing import Optional
import asyncpg

from app.dto.invoice_item import InvoiceItemCreate, InvoiceItemUpdate, InvoiceItemRead


async def create_invoice_item(
    conn: asyncpg.Connection,
    data: InvoiceItemCreate,
    created_by: Optional[str] = None,
) -> InvoiceItemRead:
    row = await conn.fetchrow(
        """
        INSERT INTO invoice_items
            (invoice_item_id, invoice_id, product_id, quantity, price, user_id, created_by, updated_by)
        VALUES ($1, $2, $3, $4, $5, $6, $6, $6)
        RETURNING invoice_item_id, invoice_id, product_id, quantity, price,
                  user_id, created_at, updated_at, created_by, updated_by
        """,
        str(uuid4()), data.invoice_id, data.product_id,
        data.quantity, data.price, created_by,
    )
    return InvoiceItemRead(**dict(row))


async def get_invoice_item(
    conn: asyncpg.Connection, invoice_item_id: str, user_id: Optional[str] = None
) -> Optional[InvoiceItemRead]:
    query = """
        SELECT invoice_item_id, invoice_id, product_id, quantity, price,
               user_id, created_at, updated_at, created_by, updated_by
        FROM invoice_items
        WHERE invoice_item_id = $1 AND deleted = FALSE
    """
    params = [invoice_item_id]
    if user_id:
        query += " AND user_id = $2"
        params.append(user_id)

    row = await conn.fetchrow(query, *params)
    return InvoiceItemRead(**dict(row)) if row else None


async def list_invoice_items(
    conn: asyncpg.Connection,
    invoice_id: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
) -> list[InvoiceItemRead]:
    query = """
        SELECT invoice_item_id, invoice_id, product_id, quantity, price,
               user_id, created_at, updated_at, created_by, updated_by
        FROM invoice_items
        WHERE deleted = FALSE
    """
    params = [limit, offset]
    if invoice_id:
        query += " AND invoice_id = $3"
        params.append(invoice_id)
    if user_id:
        query += f" AND user_id = ${len(params) + 1}"
        params.append(user_id)

    query += " ORDER BY created_at LIMIT $1 OFFSET $2"
    rows = await conn.fetch(query, *params)
    return [InvoiceItemRead(**dict(r)) for r in rows]


async def update_invoice_item(
    conn: asyncpg.Connection,
    invoice_item_id: str,
    data: InvoiceItemUpdate,
    updated_by: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Optional[InvoiceItemRead]:
    query = """
        UPDATE invoice_items
        SET
            quantity   = COALESCE($1, quantity),
            price      = COALESCE($2, price),
            updated_by = $3,
            updated_at = CURRENT_TIMESTAMP
        WHERE invoice_item_id = $4 AND deleted = FALSE
    """
    params = [data.quantity, data.price, updated_by, invoice_item_id]
    if user_id:
        query += " AND user_id = $5"
        params.append(user_id)

    query += " RETURNING invoice_item_id, invoice_id, product_id, quantity, price, user_id, created_at, updated_at, created_by, updated_by"
    row = await conn.fetchrow(query, *params)
    return InvoiceItemRead(**dict(row)) if row else None


async def delete_invoice_item(
    conn: asyncpg.Connection,
    invoice_item_id: str,
    deleted_by: Optional[str] = None,
    user_id: Optional[str] = None,
) -> bool:
    query = """
        UPDATE invoice_items
        SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
        WHERE invoice_item_id = $1 AND deleted = FALSE
    """
    params = [invoice_item_id, deleted_by]
    if user_id:
        query += " AND user_id = $3"
        params.append(user_id)

    result = await conn.execute(query, *params)
    return result == "UPDATE 1"
