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
            (invoice_item_id, invoice_id, product_id, quantity, price, created_by, updated_by)
        VALUES ($1, $2, $3, $4, $5, $6, $6)
        RETURNING invoice_item_id, invoice_id, product_id, quantity, price,
                  created_at, updated_at, created_by, updated_by
        """,
        str(uuid4()), data.invoice_id, data.product_id,
        data.quantity, data.price, created_by,
    )
    return InvoiceItemRead(**dict(row))


async def get_invoice_item(
    conn: asyncpg.Connection, invoice_item_id: str
) -> Optional[InvoiceItemRead]:
    row = await conn.fetchrow(
        """
        SELECT invoice_item_id, invoice_id, product_id, quantity, price,
               created_at, updated_at, created_by, updated_by
        FROM invoice_items
        WHERE invoice_item_id = $1 AND deleted = FALSE
        """,
        invoice_item_id,
    )
    return InvoiceItemRead(**dict(row)) if row else None


async def list_invoice_items(
    conn: asyncpg.Connection,
    invoice_id: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
) -> list[InvoiceItemRead]:
    if invoice_id:
        rows = await conn.fetch(
            """
            SELECT invoice_item_id, invoice_id, product_id, quantity, price,
                   created_at, updated_at, created_by, updated_by
            FROM invoice_items
            WHERE invoice_id = $1 AND deleted = FALSE
            ORDER BY created_at
            LIMIT $2 OFFSET $3
            """,
            invoice_id, limit, offset,
        )
    else:
        rows = await conn.fetch(
            """
            SELECT invoice_item_id, invoice_id, product_id, quantity, price,
                   created_at, updated_at, created_by, updated_by
            FROM invoice_items
            WHERE deleted = FALSE
            ORDER BY created_at
            LIMIT $1 OFFSET $2
            """,
            limit, offset,
        )
    return [InvoiceItemRead(**dict(r)) for r in rows]


async def update_invoice_item(
    conn: asyncpg.Connection,
    invoice_item_id: str,
    data: InvoiceItemUpdate,
    updated_by: Optional[str] = None,
) -> Optional[InvoiceItemRead]:
    row = await conn.fetchrow(
        """
        UPDATE invoice_items
        SET
            quantity   = COALESCE($1, quantity),
            price      = COALESCE($2, price),
            updated_by = $3,
            updated_at = CURRENT_TIMESTAMP
        WHERE invoice_item_id = $4 AND deleted = FALSE
        RETURNING invoice_item_id, invoice_id, product_id, quantity, price,
                  created_at, updated_at, created_by, updated_by
        """,
        data.quantity, data.price, updated_by, invoice_item_id,
    )
    return InvoiceItemRead(**dict(row)) if row else None


async def delete_invoice_item(
    conn: asyncpg.Connection,
    invoice_item_id: str,
    deleted_by: Optional[str] = None,
) -> bool:
    result = await conn.execute(
        """
        UPDATE invoice_items
        SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
        WHERE invoice_item_id = $1 AND deleted = FALSE
        """,
        invoice_item_id, deleted_by,
    )
    return result == "UPDATE 1"