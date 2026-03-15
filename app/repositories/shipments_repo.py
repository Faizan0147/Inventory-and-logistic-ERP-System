from uuid import uuid4
from typing import Optional
import asyncpg

from app.dto.shipments import ShipmentCreate, ShipmentUpdate, ShipmentRead


async def create_shipment(
    conn: asyncpg.Connection,
    data: ShipmentCreate,
    created_by: Optional[str] = None,
) -> ShipmentRead:
    row = await conn.fetchrow(
        """
        INSERT INTO shipments
            (shipment_id, po_id, warehouse_id, carrier_name, tracking_number,
             shipment_date, estimated_arrival, status, created_by, updated_by)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $9)
        RETURNING shipment_id, po_id, warehouse_id, carrier_name, tracking_number,
                  shipment_date, estimated_arrival, actual_arrival, status,
                  created_at, updated_at, created_by, updated_by
        """,
        str(uuid4()), data.po_id, data.warehouse_id, data.carrier_name,
        data.tracking_number, data.shipment_date, data.estimated_arrival,
        data.status, created_by,
    )
    return ShipmentRead(**dict(row))


async def get_shipment(
    conn: asyncpg.Connection, shipment_id: str
) -> Optional[ShipmentRead]:
    row = await conn.fetchrow(
        """
        SELECT shipment_id, po_id, warehouse_id, carrier_name, tracking_number,
               shipment_date, estimated_arrival, actual_arrival, status,
               created_at, updated_at, created_by, updated_by
        FROM shipments
        WHERE shipment_id = $1 AND deleted = FALSE
        """,
        shipment_id,
    )
    return ShipmentRead(**dict(row)) if row else None


async def list_shipments(
    conn: asyncpg.Connection,
    offset: int = 0,
    limit: int = 100,
) -> list[ShipmentRead]:
    rows = await conn.fetch(
        """
        SELECT shipment_id, po_id, warehouse_id, carrier_name, tracking_number,
               shipment_date, estimated_arrival, actual_arrival, status,
               created_at, updated_at, created_by, updated_by
        FROM shipments
        WHERE deleted = FALSE
        ORDER BY created_at DESC
        LIMIT $1 OFFSET $2
        """,
        limit, offset,
    )
    return [ShipmentRead(**dict(r)) for r in rows]


async def update_shipment(
    conn: asyncpg.Connection,
    shipment_id: str,
    data: ShipmentUpdate,
    updated_by: Optional[str] = None,
) -> Optional[ShipmentRead]:
    row = await conn.fetchrow(
        """
        UPDATE shipments
        SET
            warehouse_id      = COALESCE($1, warehouse_id),
            carrier_name      = COALESCE($2, carrier_name),
            tracking_number   = COALESCE($3, tracking_number),
            shipment_date     = COALESCE($4, shipment_date),
            estimated_arrival = COALESCE($5, estimated_arrival),
            actual_arrival    = COALESCE($6, actual_arrival),
            status            = COALESCE($7, status),
            updated_by        = $8,
            updated_at        = CURRENT_TIMESTAMP
        WHERE shipment_id = $9 AND deleted = FALSE
        RETURNING shipment_id, po_id, warehouse_id, carrier_name, tracking_number,
                  shipment_date, estimated_arrival, actual_arrival, status,
                  created_at, updated_at, created_by, updated_by
        """,
        data.warehouse_id, data.carrier_name, data.tracking_number,
        data.shipment_date, data.estimated_arrival, data.actual_arrival,
        data.status, updated_by, shipment_id,
    )
    return ShipmentRead(**dict(row)) if row else None


async def delete_shipment(
    conn: asyncpg.Connection,
    shipment_id: str,
    deleted_by: Optional[str] = None,
) -> bool:
    result = await conn.execute(
        """
        UPDATE shipments
        SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
        WHERE shipment_id = $1 AND deleted = FALSE
        """,
        shipment_id, deleted_by,
    )
    return result == "UPDATE 1"