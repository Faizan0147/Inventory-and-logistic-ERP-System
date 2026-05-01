import logging
from typing import Optional
import asyncpg
from uuid import uuid4

from app.dto.poi import (
    POItemCreate,
    POItemRead,
    POItemUpdate,
    PurchaseOrderSummary,
    ProductSummary,
)

logger = logging.getLogger(__name__)

_SELECT = """
    SELECT
        pi.po_item_id, pi.po_id, pi.product_id, pi.user_id,
        pi.quantity, pi.price,
        pi.created_at, pi.updated_at, pi.created_by, pi.updated_by,
        po.order_number, po.order_date, po.status AS po_status,
        p.product_name, p.sku, p.price AS product_price
    FROM purchase_order_items pi
    LEFT JOIN purchase_orders po ON po.po_id = pi.po_id AND po.deleted = FALSE
    LEFT JOIN products p ON p.product_id = pi.product_id AND p.deleted = FALSE
"""


def _build(row: asyncpg.Record) -> POItemRead:
    d = dict(row)
    purchase_order = None
    if d.get("order_number") is not None or d.get("order_date") is not None:
        purchase_order = PurchaseOrderSummary(
            po_id=d["po_id"],
            order_number=d.get("order_number"),
            order_date=d.get("order_date"),
            status=d.get("po_status"),
        )
    product = None
    if d.get("product_name"):
        product = ProductSummary(
            product_id=d["product_id"],
            product_name=d["product_name"],
            sku=d["sku"],
            price=d.get("product_price"),
        )
    return POItemRead(
        po_item_id=d["po_item_id"],
        po_id=d["po_id"],
        product_id=d["product_id"],
        user_id=d["user_id"],
        quantity=d["quantity"],
        price=d.get("price"),
        purchase_order=purchase_order,
        product=product,
        created_at=d.get("created_at"),
        updated_at=d.get("updated_at"),
        created_by=d.get("created_by"),
        updated_by=d.get("updated_by"),
    )


async def create_po_item(
    conn: asyncpg.Connection,
    data: POItemCreate,
    user_id: str,
    created_by: Optional[str] = None,
) -> POItemRead:
    try:
        row = await conn.fetchrow(
            """
            INSERT INTO purchase_order_items (
                po_item_id, po_id, product_id, quantity, price, user_id, created_by, updated_by
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $7)
            RETURNING po_item_id
            """,
            str(uuid4()), data.po_id, data.product_id,
            data.quantity, data.price, user_id, created_by,
        )
        return await get_po_item(conn, row["po_item_id"])

    except asyncpg.ForeignKeyViolationError as e:
        logger.warning("create_po_item: foreign key violation — %s", e)
        raise ValueError("Invalid po_id or product_id.")
    except asyncpg.CheckViolationError as e:
        logger.warning("create_po_item: check constraint violation — %s", e)
        raise ValueError("Quantity must be greater than 0.")
    except asyncpg.PostgresError as e:
        logger.error("create_po_item: database error — %s", e)
        raise RuntimeError(f"Database error while creating purchase order item: {e}")


async def get_po_item(
    conn: asyncpg.Connection,
    po_item_id: str,
    user_id: Optional[str] = None,
) -> Optional[POItemRead]:
    try:
        query = _SELECT + " WHERE pi.po_item_id = $1 AND pi.deleted = FALSE"
        params = [po_item_id]
        if user_id:
            query += " AND pi.user_id = $2"
            params.append(user_id)
        row = await conn.fetchrow(query, *params)
        return _build(row) if row else None
    except asyncpg.PostgresError as e:
        logger.error("get_po_item(%s): database error — %s", po_item_id, e)
        raise RuntimeError(f"Database error while fetching purchase order item: {e}")


async def list_po_items(
    conn: asyncpg.Connection,
    po_id: str,
    user_id: Optional[str] = None,
) -> list[POItemRead]:
    try:
        query = _SELECT + " WHERE pi.po_id = $1 AND pi.deleted = FALSE"
        params = [po_id]
        if user_id:
            query += " AND pi.user_id = $2"
            params.append(user_id)
        rows = await conn.fetch(query, *params)
        return [_build(r) for r in rows]
    except asyncpg.PostgresError as e:
        logger.error("list_po_items(%s): database error — %s", po_id, e)
        raise RuntimeError(f"Database error while listing purchase order items: {e}")


async def update_po_item(
    conn: asyncpg.Connection,
    po_item_id: str,
    data: POItemUpdate,
    updated_by: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Optional[POItemRead]:
    try:
        query = """
            UPDATE purchase_order_items
            SET
                po_id      = COALESCE($1, po_id),
                product_id = COALESCE($2, product_id),
                quantity   = COALESCE($3, quantity),
                price      = COALESCE($4, price),
                updated_by = $5,
                updated_at = CURRENT_TIMESTAMP
            WHERE po_item_id = $6 AND deleted = FALSE
        """
        params = [data.po_id, data.product_id, data.quantity, data.price, updated_by, po_item_id]
        if user_id:
            query += " AND user_id = $7"
            params.append(user_id)
        query += " RETURNING po_item_id"
        row = await conn.fetchrow(query, *params)
        if not row:
            return None
        return await get_po_item(conn, row["po_item_id"])

    except asyncpg.ForeignKeyViolationError as e:
        logger.warning("update_po_item(%s): foreign key violation — %s", po_item_id, e)
        raise ValueError("Invalid po_id or product_id.")
    except asyncpg.CheckViolationError as e:
        logger.warning("update_po_item(%s): check constraint violation — %s", po_item_id, e)
        raise ValueError("Quantity must be greater than 0.")
    except asyncpg.PostgresError as e:
        logger.error("update_po_item(%s): database error — %s", po_item_id, e)
        raise RuntimeError(f"Database error while updating purchase order item: {e}")


async def delete_po_item(
    conn: asyncpg.Connection,
    po_item_id: str,
    deleted_by: Optional[str] = None,
    user_id: Optional[str] = None,
) -> bool:
    try:
        query = """
            UPDATE purchase_order_items
            SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
            WHERE po_item_id = $1 AND deleted = FALSE
        """
        params = [po_item_id, deleted_by]
        if user_id:
            query += " AND user_id = $3"
            params.append(user_id)
        result = await conn.execute(query, *params)
        return result == "UPDATE 1"
    except asyncpg.PostgresError as e:
        logger.error("delete_po_item(%s): database error — %s", po_item_id, e)
        raise RuntimeError(f"Database error while deleting purchase order item: {e}")
