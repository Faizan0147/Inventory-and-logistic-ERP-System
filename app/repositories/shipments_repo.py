import logging
from uuid import uuid4
from typing import Optional
import asyncpg

from app.dto.shipments import (
    ShipmentCreate,
    ShipmentUpdate,
    ShipmentRead,
    PurchaseOrderSummary,
    WarehouseSummary,
)

logger = logging.getLogger(__name__)

_SELECT = """
    SELECT
        s.shipment_id, s.po_id, s.user_id, s.warehouse_id,
        s.carrier_name, s.tracking_number, s.shipment_date,
        s.estimated_arrival, s.actual_arrival, s.status, s.notes,
        s.created_at, s.updated_at, s.created_by, s.updated_by,
        po.order_number, po.order_date, po.status AS po_status, po.supplier_id,
        w.warehouse_name, w.location, w.city
    FROM shipments s
    LEFT JOIN purchase_orders po ON po.po_id = s.po_id AND po.deleted = FALSE
    LEFT JOIN warehouses w ON w.warehouse_id = s.warehouse_id AND w.deleted = FALSE
"""


def _build(row: asyncpg.Record) -> ShipmentRead:
    d = dict(row)
    purchase_order = None
    if d.get("order_number") is not None or d.get("order_date") is not None:
        purchase_order = PurchaseOrderSummary(
            po_id=d["po_id"],
            order_number=d.get("order_number"),
            order_date=d.get("order_date"),
            status=d.get("po_status"),
            supplier_id=d.get("supplier_id"),
        )
    warehouse = None
    if d.get("warehouse_name"):
        warehouse = WarehouseSummary(
            warehouse_id=d["warehouse_id"],
            warehouse_name=d["warehouse_name"],
            location=d.get("location"),
            city=d.get("city"),
        )
    return ShipmentRead(
        shipment_id=d["shipment_id"],
        po_id=d["po_id"],
        user_id=d["user_id"],
        warehouse_id=d.get("warehouse_id"),
        carrier_name=d.get("carrier_name"),
        tracking_number=d.get("tracking_number"),
        shipment_date=d.get("shipment_date"),
        estimated_arrival=d.get("estimated_arrival"),
        actual_arrival=d.get("actual_arrival"),
        status=d.get("status"),
        notes=d.get("notes"),
        purchase_order=purchase_order,
        warehouse=warehouse,
        created_at=d.get("created_at"),
        updated_at=d.get("updated_at"),
        created_by=d.get("created_by"),
        updated_by=d.get("updated_by"),
    )


async def create_shipment(
    conn: asyncpg.Connection,
    data: ShipmentCreate,
    user_id: str,
    created_by: Optional[str] = None,
) -> ShipmentRead:
    try:
        row = await conn.fetchrow(
            """
            INSERT INTO shipments (
                shipment_id, po_id, warehouse_id, user_id,
                carrier_name, tracking_number, shipment_date,
                estimated_arrival, status, notes, created_by, updated_by
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $11)
            RETURNING shipment_id
            """,
            str(uuid4()),
            data.purchase_order_id,
            data.warehouse_id,
            user_id,
            data.carrier_name,
            data.tracking_number,
            data.shipment_date,
            data.estimated_arrival,
            data.status,
            data.notes,
            created_by,
        )
        return await get_shipment(conn, row["shipment_id"])

    except asyncpg.UniqueViolationError:
        logger.warning(
            "create_shipment: duplicate tracking_number '%s'", data.tracking_number
        )
        raise ValueError(
            f"A shipment with tracking number '{data.tracking_number}' already exists."
        )
    except asyncpg.ForeignKeyViolationError as e:
        logger.warning("create_shipment: foreign key violation — %s", e)
        raise ValueError("Invalid purchase_order_id or warehouse_id.")
    except asyncpg.PostgresError as e:
        logger.error("create_shipment: database error — %s", e)
        raise RuntimeError(f"Database error while creating shipment: {e}")


async def get_shipment(
    conn: asyncpg.Connection,
    shipment_id: str,
    user_id: Optional[str] = None,
) -> Optional[ShipmentRead]:
    try:
        query = _SELECT + " WHERE s.shipment_id = $1 AND s.deleted = FALSE"
        params = [shipment_id]
        if user_id:
            query += " AND s.user_id = $2"
            params.append(user_id)
        row = await conn.fetchrow(query, *params)
        return _build(row) if row else None
    except asyncpg.PostgresError as e:
        logger.error("get_shipment(%s): database error — %s", shipment_id, e)
        raise RuntimeError(f"Database error while fetching shipment: {e}")


async def list_shipments(
    conn: asyncpg.Connection,
    offset: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
) -> list[ShipmentRead]:
    try:
        query = _SELECT + " WHERE s.deleted = FALSE"
        params = [limit, offset]
        if user_id:
            query += " AND s.user_id = $3"
            params.append(user_id)
        query += " ORDER BY s.created_at DESC LIMIT $1 OFFSET $2"
        rows = await conn.fetch(query, *params)
        return [_build(r) for r in rows]
    except asyncpg.PostgresError as e:
        logger.error("list_shipments: database error — %s", e)
        raise RuntimeError(f"Database error while listing shipments: {e}")


async def update_shipment(
    conn: asyncpg.Connection,
    shipment_id: str,
    data: ShipmentUpdate,
    updated_by: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Optional[ShipmentRead]:
    try:
        query = """
            UPDATE shipments
            SET
                warehouse_id      = COALESCE($1,  warehouse_id),
                carrier_name      = COALESCE($2,  carrier_name),
                tracking_number   = COALESCE($3,  tracking_number),
                shipment_date     = COALESCE($4,  shipment_date),
                estimated_arrival = COALESCE($5,  estimated_arrival),
                actual_arrival    = COALESCE($6,  actual_arrival),
                status            = COALESCE($7,  status),
                notes             = COALESCE($8,  notes),
                updated_by        = $9,
                updated_at        = CURRENT_TIMESTAMP
            WHERE shipment_id = $10 AND deleted = FALSE
        """
        params = [
            data.warehouse_id,
            data.carrier_name,
            data.tracking_number,
            data.shipment_date,
            data.estimated_arrival,
            data.actual_arrival,
            data.status,
            data.notes,
            updated_by,
            shipment_id,
        ]
        if user_id:
            query += " AND user_id = $11"
            params.append(user_id)
        query += " RETURNING shipment_id"
        row = await conn.fetchrow(query, *params)
        if not row:
            return None
        return await get_shipment(conn, row["shipment_id"])

    except asyncpg.UniqueViolationError:
        logger.warning(
            "update_shipment(%s): duplicate tracking_number '%s'",
            shipment_id,
            data.tracking_number,
        )
        raise ValueError(
            f"A shipment with tracking number '{data.tracking_number}' already exists."
        )
    except asyncpg.ForeignKeyViolationError as e:
        logger.warning(
            "update_shipment(%s): foreign key violation — %s", shipment_id, e
        )
        raise ValueError("Invalid warehouse_id.")
    except asyncpg.PostgresError as e:
        logger.error("update_shipment(%s): database error — %s", shipment_id, e)
        raise RuntimeError(f"Database error while updating shipment: {e}")


async def delete_shipment(
    conn: asyncpg.Connection,
    shipment_id: str,
    deleted_by: Optional[str] = None,
    user_id: Optional[str] = None,
) -> bool:
    try:
        query = """
            UPDATE shipments
            SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
            WHERE shipment_id = $1 AND deleted = FALSE
        """
        params = [shipment_id, deleted_by]
        if user_id:
            query += " AND user_id = $3"
            params.append(user_id)
        result = await conn.execute(query, *params)
        return result == "UPDATE 1"
    except asyncpg.PostgresError as e:
        logger.error("delete_shipment(%s): database error — %s", shipment_id, e)
        raise RuntimeError(f"Database error while deleting shipment: {e}")
