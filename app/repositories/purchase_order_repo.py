from uuid import uuid4
from typing import Optional
import asyncpg

from app.dto.purchase_order import (
    PurchaseOrderCreate, PurchaseOrderRead, PurchaseOrderUpdate,
)


async def create_purchase_order(
    conn: asyncpg.Connection, data: PurchaseOrderCreate, created_by: Optional[str] = None
) -> PurchaseOrderRead:
    row = await conn.fetchrow(
        """
        INSERT INTO purchase_orders (po_id, supplier_id, warehouse_id, order_number, order_date, expected_delivery, total_amount, status, created_by, updated_by)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $9)
        RETURNING po_id, supplier_id, warehouse_id, order_number, order_date, expected_delivery,
                  total_amount, status, created_at, updated_at, created_by, updated_by
        """,
        str(uuid4()), data.supplier_id, data.warehouse_id, data.order_number,
        data.order_date, data.expected_delivery, data.total_amount, data.status, created_by,
    )
    return PurchaseOrderRead(**dict(row))


async def get_purchase_order(conn: asyncpg.Connection, po_id: str) -> Optional[PurchaseOrderRead]:
    row = await conn.fetchrow(
        """
        SELECT po_id, supplier_id, warehouse_id, order_number, order_date, expected_delivery,
               total_amount, status, created_at, updated_at, created_by, updated_by
        FROM purchase_orders
        WHERE po_id = $1 AND deleted = FALSE
        """,
        po_id,
    )
    if not row:
        return None
    return PurchaseOrderRead(**dict(row))


async def list_purchase_orders(
    conn: asyncpg.Connection, offset: int = 0, limit: int = 100
) -> list[PurchaseOrderRead]:
    rows = await conn.fetch(
        """
        SELECT po_id, supplier_id, warehouse_id, order_number, order_date, expected_delivery,
               total_amount, status, created_at, updated_at, created_by, updated_by
        FROM purchase_orders
        WHERE deleted = FALSE
        ORDER BY order_date DESC
        LIMIT $1 OFFSET $2
        """,
        limit, offset,
    )
    return [PurchaseOrderRead(**dict(r)) for r in rows]


async def update_purchase_order(
    conn: asyncpg.Connection, po_id: str, data: PurchaseOrderUpdate, updated_by: Optional[str] = None
) -> Optional[PurchaseOrderRead]:
    row = await conn.fetchrow(
        """
        UPDATE purchase_orders
        SET
            supplier_id = COALESCE($1, supplier_id),
            warehouse_id = COALESCE($2, warehouse_id),
            order_number = COALESCE($3, order_number),
            order_date = COALESCE($4, order_date),
            expected_delivery = COALESCE($5, expected_delivery),
            total_amount = COALESCE($6, total_amount),
            status = COALESCE($7, status),
            updated_by = $8,
            updated_at = CURRENT_TIMESTAMP
        WHERE po_id = $9 AND deleted = FALSE
        RETURNING po_id, supplier_id, warehouse_id, order_number, order_date, expected_delivery,
                  total_amount, status, created_at, updated_at, created_by, updated_by
        """,
        data.supplier_id, data.warehouse_id, data.order_number, data.order_date,
        data.expected_delivery, data.total_amount, data.status, updated_by, po_id,
    )
    return PurchaseOrderRead(**dict(row)) if row else None


async def delete_purchase_order(
    conn: asyncpg.Connection, po_id: str, deleted_by: Optional[str] = None
) -> bool:
    result = await conn.execute(
        """
        UPDATE purchase_orders
        SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
        WHERE po_id = $1 AND deleted = FALSE
        """,
        po_id, deleted_by,
    )
    return result == "UPDATE 1"
