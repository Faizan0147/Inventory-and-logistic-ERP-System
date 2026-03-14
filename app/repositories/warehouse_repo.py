from uuid import uuid4
from typing import Optional
import asyncpg

from app.dto.warehouse import (
    WarehouseCreate,
    WarehouseRead,
    WarehouseUpdate
)


async def create_warehouse(
    conn: asyncpg.Connection, data: WarehouseCreate, created_by: Optional[str] = None
) -> WarehouseRead:
    row = await conn.fetchrow(
        """
        INSERT INTO warehouses (warehouse_id, warehouse_name, location, city, capacity, phone, manager_id, is_active, created_by, updated_by)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $9)
        RETURNING warehouse_id, warehouse_name, location, city, capacity, phone, manager_id, is_active,
                  created_at, updated_at, created_by, updated_by
        """,
        str(uuid4()), data.warehouse_name, data.location, data.city,
        data.capacity, data.phone, data.manager_id, data.is_active, created_by,
    )
    return WarehouseRead(**dict(row))


async def get_warehouse(conn: asyncpg.Connection, warehouse_id: str) -> Optional[WarehouseRead]:
    row = await conn.fetchrow(
        """
        SELECT warehouse_id, warehouse_name, location, city, capacity, phone, manager_id, is_active,
               created_at, updated_at, created_by, updated_by
        FROM warehouses
        WHERE warehouse_id = $1 AND deleted = FALSE
        """,
        warehouse_id,
    )
    if not row:
        return None
    return WarehouseRead(**dict(row))


async def list_warehouses(
    conn: asyncpg.Connection, offset: int = 0, limit: int = 100
) -> list[WarehouseRead]:
    rows = await conn.fetch(
        """
        SELECT warehouse_id, warehouse_name, location, city, capacity, phone, manager_id, is_active,
               created_at, updated_at, created_by, updated_by
        FROM warehouses
        WHERE deleted = FALSE
        ORDER BY warehouse_name
        LIMIT $1 OFFSET $2
        """,
        limit, offset,
    )
    return [WarehouseRead(**dict(r)) for r in rows]


async def update_warehouse(
    conn: asyncpg.Connection, warehouse_id: str, data: WarehouseUpdate, updated_by: Optional[str] = None
) -> Optional[WarehouseRead]:
    row = await conn.fetchrow(
        """
        UPDATE warehouses
        SET
            warehouse_name = COALESCE($1, warehouse_name),
            location = COALESCE($2, location),
            city = COALESCE($3, city),
            capacity = COALESCE($4, capacity),
            phone = COALESCE($5, phone),
            manager_id = COALESCE($6, manager_id),
            is_active = COALESCE($7, is_active),
            updated_by = $8,
            updated_at = CURRENT_TIMESTAMP
        WHERE warehouse_id = $9 AND deleted = FALSE
        RETURNING warehouse_id, warehouse_name, location, city, capacity, phone, manager_id, is_active,
                  created_at, updated_at, created_by, updated_by
        """,
        data.warehouse_name, data.location, data.city, data.capacity,
        data.phone, data.manager_id, data.is_active, updated_by, warehouse_id,
    )
    return WarehouseRead(**dict(row)) if row else None


async def delete_warehouse(
    conn: asyncpg.Connection, warehouse_id: str, deleted_by: Optional[str] = None
) -> bool:
    result = await conn.execute(
        """
        UPDATE warehouses
        SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
        WHERE warehouse_id = $1 AND deleted = FALSE
        """,
        warehouse_id, deleted_by,
    )
    return result == "UPDATE 1"