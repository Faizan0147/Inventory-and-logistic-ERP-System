import logging
from uuid import uuid4
from typing import Optional
import asyncpg

from app.dto.invoice_item import (
    InvoiceItemCreate,
    InvoiceItemUpdate,
    InvoiceItemRead,
    InvoiceSummary,
    ProductSummary,
)

logger = logging.getLogger(__name__)

_SELECT = """
    SELECT
        ii.invoice_item_id, ii.invoice_id, ii.product_id, ii.user_id,
        ii.quantity, ii.price,
        ii.created_at, ii.updated_at, ii.created_by, ii.updated_by,
        i.invoice_number, i.invoice_date, i.total_amount, i.status AS invoice_status,
        p.product_name, p.sku, p.price AS product_price
    FROM invoice_items ii
    LEFT JOIN invoices i ON i.invoice_id = ii.invoice_id AND i.deleted = FALSE
    LEFT JOIN products p ON p.product_id = ii.product_id AND p.deleted = FALSE
"""


def _build(row: asyncpg.Record) -> InvoiceItemRead:
    d = dict(row)
    invoice = None
    if d.get("invoice_number") is not None or d.get("invoice_date") is not None:
        invoice = InvoiceSummary(
            invoice_id=d["invoice_id"],
            invoice_number=d.get("invoice_number"),
            invoice_date=d.get("invoice_date"),
            total_amount=d.get("total_amount"),
            status=d.get("invoice_status"),
        )
    product = None
    if d.get("product_name"):
        product = ProductSummary(
            product_id=d["product_id"],
            product_name=d["product_name"],
            sku=d["sku"],
            price=d.get("product_price"),
        )

    return InvoiceItemRead(
        invoice_item_id=d["invoice_item_id"],
        invoice_id=d["invoice_id"],
        product_id=d["product_id"],
        user_id=d["user_id"],
        quantity=d.get("quantity"),
        price=d.get("price"),
        invoice=invoice,
        product=product,
        created_at=d.get("created_at"),
        updated_at=d.get("updated_at"),
        created_by=d.get("created_by"),
        updated_by=d.get("updated_by"),
    )


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
            VALUES ($1, $2, $3, $4, $5, $6, $7, $7)
            RETURNING invoice_item_id
            """,
            str(uuid4()),
            data.invoice_id,
            data.product_id,
            data.quantity,
            data.price,
            user_id,
            created_by,
        )
        return await get_invoice_item(conn, row["invoice_item_id"])

    except asyncpg.ForeignKeyViolationError as e:
        logger.warning("create_invoice_item: foreign key violation — %s", e)
        raise ValueError("Invalid invoice_id or product_id.")
    except asyncpg.PostgresError as e:
        logger.error("create_invoice_item: database error — %s", e)
        raise RuntimeError(f"Database error while creating invoice item: {e}")


async def get_invoice_item(
    conn: asyncpg.Connection,
    invoice_item_id: str,
    user_id: Optional[str] = None,
) -> Optional[InvoiceItemRead]:
    try:
        query = _SELECT + " WHERE ii.invoice_item_id = $1 AND ii.deleted = FALSE"
        params = [invoice_item_id]
        if user_id:
            query += " AND ii.user_id = $2"
            params.append(user_id)
        row = await conn.fetchrow(query, *params)
        return _build(row) if row else None
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
        query = _SELECT + " WHERE ii.deleted = FALSE"
        params: list = [limit, offset]
        if invoice_id:
            query += " AND ii.invoice_id = $3"
            params.append(invoice_id)
        if user_id:
            query += f" AND ii.user_id = ${len(params) + 1}"
            params.append(user_id)
        query += " ORDER BY ii.created_at LIMIT $1 OFFSET $2"
        rows = await conn.fetch(query, *params)
        return [_build(r) for r in rows]
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
        query += " RETURNING invoice_item_id"
        row = await conn.fetchrow(query, *params)
        if not row:
            return None
        return await get_invoice_item(conn, row["invoice_item_id"])

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
