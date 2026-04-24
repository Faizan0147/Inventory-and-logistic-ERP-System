import logging
from uuid import uuid4
from typing import Optional
import asyncpg

from app.dto.invoice_item import InvoiceItemCreate, InvoiceItemUpdate, InvoiceItemRead

logger = logging.getLogger(__name__)


async def create_invoice_item(
    conn: asyncpg.Connection,
    data: InvoiceItemCreate,
    user_id: str,
    created_by: Optional[str] = None,
) -> InvoiceItemRead:
    try:
        row = await conn.fetchrow(
            """
            INSERT INTO invoice_items (
                invoice_item_id, invoice_id, product_id, quantity, price, 
                user_id, created_by, updated_by
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING invoice_item_id, invoice_id, product_id, quantity, price,
                      user_id, created_at, updated_at, created_by, updated_by
            """,
            str(uuid4()), 
            data.invoice_id, 
            data.product_id,
            data.quantity, 
            data.price, 
            user_id,
            created_by,
            created_by,
        )
        return InvoiceItemRead(**dict(row))

    except asyncpg.ForeignKeyViolationError as e:
        logger.warning("create_invoice_item: foreign key violation — %s", e)
        raise ValueError("Invalid invoice_id or product_id.")

    except asyncpg.PostgresError as e:
        logger.error("create_invoice_item: database error — %s", e)
        raise RuntimeError(f"Database error while creating invoice item: {e}")


async def get_invoice_item(
    conn: asyncpg.Connection, 
    invoice_item_id: str, 
    user_id: Optional[str] = None
) -> Optional[InvoiceItemRead]:
    try:
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

    except asyncpg.PostgresError as e:
        logger.error("get_invoice_item(%s): database error — %s", invoice_item_id, e)
        raise RuntimeError(f"Database error while fetching invoice item: {e}")


async def list_invoice_items(
    conn: asyncpg.Connection,
    invoice_id: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
) -> list[InvoiceItemRead]:
    try:
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

    except asyncpg.PostgresError as e:
        logger.error("list_invoice_items: database error — %s", e)
        raise RuntimeError(f"Database error while listing invoice items: {e}")


async def update_invoice_item(
    conn: asyncpg.Connection,
    invoice_item_id: str,
    data: InvoiceItemUpdate,
    updated_by: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Optional[InvoiceItemRead]:
    try:
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

        query += """
            RETURNING invoice_item_id, invoice_id, product_id, quantity, price, 
                      user_id, created_at, updated_at, created_by, updated_by
        """
        row = await conn.fetchrow(query, *params)
        return InvoiceItemRead(**dict(row)) if row else None

    except asyncpg.PostgresError as e:
        logger.error("update_invoice_item(%s): database error — %s", invoice_item_id, e)
        raise RuntimeError(f"Database error while updating invoice item: {e}")


async def delete_invoice_item(
    conn: asyncpg.Connection,
    invoice_item_id: str,
    deleted_by: Optional[str] = None,
    user_id: Optional[str] = None,
) -> bool:
    try:
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

    except asyncpg.PostgresError as e:
        logger.error("delete_invoice_item(%s): database error — %s", invoice_item_id, e)
        raise RuntimeError(f"Database error while deleting invoice item: {e}")
