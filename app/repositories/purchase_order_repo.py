import logging
from uuid import uuid4
from typing import Optional
import asyncpg

from app.dto.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderRead,
    PurchaseOrderUpdate,
    SupplierSummary,
    WarehouseSummary,
)

logger = logging.getLogger(__name__)


def _build(row: asyncpg.Record) -> PurchaseOrderRead:
    d = dict(row)

    supplier = None
    
    if d.get("supplier_name"):
        supplier = SupplierSummary(
            supplier_id=d["supplier_id"],
            supplier_name=d["supplier_name"],
            contact_email=d.get("contact_email"),
            contact_phone=d.get("contact_phone"),
        )
    warehouse = None
    if d.get("warehouse_name"):
        warehouse = WarehouseSummary(
            warehouse_id=d["warehouse_id"],
            warehouse_name=d["warehouse_name"],
            location=d.get("location"),
            city=d.get("city"),
        )
    return PurchaseOrderRead(
        po_id=d["po_id"],
        supplier_id=d["supplier_id"],
        user_id=d["user_id"],
        warehouse_id=d.get("warehouse_id"),
        order_number=d.get("order_number"),
        order_date=d.get("order_date"),
        expected_delivery=d.get("expected_delivery"),
        total_amount=d.get("total_amount"),
        status=d.get("status"),
        supplier=supplier,
        warehouse=warehouse,
        created_at=d.get("created_at"),
        updated_at=d.get("updated_at"),
        created_by=d.get("created_by"),
        updated_by=d.get("updated_by"),
    )


async def create_purchase_order(
    conn: asyncpg.Connection,
    data: PurchaseOrderCreate,
    user_id: str,
    created_by: Optional[str] = None,
) -> PurchaseOrderRead:
    try:
        row = await conn.fetchrow(
            """
            INSERT INTO purchase_orders (
                po_id, supplier_id, warehouse_id, order_number, order_date,
                expected_delivery, total_amount, status, user_id, created_by, updated_by
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $10)
            RETURNING po_id
            """,
            str(uuid4()), data.supplier_id, data.warehouse_id, data.order_number,
            data.order_date, data.expected_delivery, data.total_amount,
            data.status, user_id, created_by,
        )
        return await get_purchase_order(conn, row["po_id"])

    except asyncpg.UniqueViolationError:
        logger.warning("create_purchase_order: duplicate order_number '%s'", data.order_number)
        raise ValueError(f"A purchase order with number '{data.order_number}' already exists.")

    except asyncpg.ForeignKeyViolationError as e:
        logger.warning("create_purchase_order: foreign key violation — %s", e)
        raise ValueError("Invalid supplier_id or warehouse_id.")

    except asyncpg.PostgresError as e:
        logger.error("create_purchase_order: database error — %s", e)
        raise RuntimeError(f"Database error while creating purchase order: {e}")


async def get_purchase_order(
    conn: asyncpg.Connection,
    po_id: str,
    user_id: Optional[str] = None,
) -> Optional[PurchaseOrderRead]:
    try:
        query = """"SELECT
        po.po_id, po.supplier_id, po.user_id, po.warehouse_id,
        po.order_number, po.order_date, po.expected_delivery,
        po.total_amount, po.status,
        po.created_at, po.updated_at, po.created_by, po.updated_by,
        s.supplier_name, s.contact_email, s.contact_phone,
        w.warehouse_name, w.location, w.city
        FROM purchase_orders po
        LEFT JOIN suppliers s ON s.supplier_id = po.supplier_id AND s.deleted = FALSE
        LEFT JOIN warehouses w ON w.warehouse_id = po.warehouse_id AND w.deleted = FALSE WHERE po.po_id = $1 AND po.deleted = FALSE"""

        params = [po_id]
        if user_id:
            query += " AND po.user_id = $2"
            params.append(user_id)
        row = await conn.fetchrow(query, *params)
        return _build(row) if row else None

    except asyncpg.PostgresError as e:
        logger.error("get_purchase_order(%s): database error — %s", po_id, e)
        raise RuntimeError(f"Database error while fetching purchase order: {e}")


async def list_purchase_orders(
    conn: asyncpg.Connection,
    offset: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
) -> list[PurchaseOrderRead]:
    try:
        query =""" SELECT
        po.po_id, po.supplier_id, po.user_id, po.warehouse_id,
        po.order_number, po.order_date, po.expected_delivery,
        po.total_amount, po.status,
        po.created_at, po.updated_at, po.created_by, po.updated_by,
        s.supplier_name, s.contact_email, s.contact_phone,
        w.warehouse_name, w.location, w.city
    FROM purchase_orders po
    LEFT JOIN suppliers s ON s.supplier_id = po.supplier_id AND s.deleted = FALSE
    LEFT JOIN warehouses w ON w.warehouse_id = po.warehouse_id AND w.deleted = FALSE 
    WHERE po.deleted = FALSE"""

        params = [limit, offset]
        if user_id:
            query += " AND po.user_id = $3"
            params.append(user_id)
        query += " ORDER BY po.order_date DESC LIMIT $1 OFFSET $2"
        rows = await conn.fetch(query, *params)
        return [_build(r) for r in rows]

    except asyncpg.PostgresError as e:
        logger.error("list_purchase_orders: database error — %s", e)
        raise RuntimeError(f"Database error while listing purchase orders: {e}")


async def update_purchase_order(
    conn: asyncpg.Connection,
    po_id: str,
    data: PurchaseOrderUpdate,
    updated_by: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Optional[PurchaseOrderRead]:
    try:
        query = """
            UPDATE purchase_orders
            SET
                supplier_id       = COALESCE($1, supplier_id),
                warehouse_id      = COALESCE($2, warehouse_id),
                order_number      = COALESCE($3, order_number),
                order_date        = COALESCE($4, order_date),
                expected_delivery = COALESCE($5, expected_delivery),
                total_amount      = COALESCE($6, total_amount),
                status            = COALESCE($7, status),
                updated_by        = $8,
                updated_at        = CURRENT_TIMESTAMP
            WHERE po_id = $9 AND deleted = FALSE
        """
        params = [
            data.supplier_id, data.warehouse_id, data.order_number, data.order_date,
            data.expected_delivery, data.total_amount, data.status, updated_by, po_id,
        ]
        
        if user_id:
            query += " AND user_id = $10"
            params.append(user_id)
        query += " RETURNING po_id"
        row = await conn.fetchrow(query, *params)

        if not row:
            return None
        return await get_purchase_order(conn, row["po_id"])

    except asyncpg.UniqueViolationError:
        logger.warning("update_purchase_order(%s): duplicate order_number '%s'", po_id, data.order_number)
        raise ValueError(f"A purchase order with number '{data.order_number}' already exists.")

    except asyncpg.ForeignKeyViolationError as e:
        logger.warning("update_purchase_order(%s): foreign key violation — %s", po_id, e)
        raise ValueError("Invalid supplier_id or warehouse_id.")
        
    except asyncpg.PostgresError as e:
        logger.error("update_purchase_order(%s): database error — %s", po_id, e)
        raise RuntimeError(f"Database error while updating purchase order: {e}")


async def delete_purchase_order(
    conn: asyncpg.Connection,
    po_id: str,
    deleted_by: Optional[str] = None,
    user_id: Optional[str] = None,
) -> bool:
    try:
        query = """
            UPDATE purchase_orders
            SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
            WHERE po_id = $1 AND deleted = FALSE
        """
        params = [po_id, deleted_by]
        if user_id:
            query += " AND user_id = $3"
            params.append(user_id)
        result = await conn.execute(query, *params)
        return result == "UPDATE 1"
    except asyncpg.PostgresError as e:
        logger.error("delete_purchase_order(%s): database error — %s", po_id, e)
        raise RuntimeError(f"Database error while deleting purchase order: {e}")
