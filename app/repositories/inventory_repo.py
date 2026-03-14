from uuid import uuid4
from typing import Optional
import asyncpg

from app.dto.inventory import (
    InventoryCreate,
    InventoryRead,
    InventoryUpdate
)


async def create_inventory(
    conn: asyncpg.Connection, data: InventoryCreate, created_by: Optional[str] = None
) -> InventoryRead:
    row = await conn.fetchrow(
        """
        INSERT INTO inventory (inventory_id, product_id, warehouse_id, quantity, reorder_level, last_restocked, created_by, updated_by)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $7)
        RETURNING inventory_id, product_id, warehouse_id, quantity, reorder_level, last_restocked,
                  created_at, updated_at, created_by, updated_by
        """,
        str(uuid4()), data.product_id, data.warehouse_id,
        data.quantity, data.reorder_level, data.last_restocked, created_by,
    )
    return InventoryRead(**dict(row))


async def get_inventory(conn: asyncpg.Connection, inventory_id: str) -> Optional[InventoryRead]:
    row = await conn.fetchrow(
        """
        SELECT inventory_id, product_id, warehouse_id, quantity, reorder_level, last_restocked, created_by, updated_by,
               created_at, updated_at
        FROM inventory
        WHERE inventory_id = $1 AND deleted = FALSE
        """,
        inventory_id,
    )
    if not row:
        return None
    return InventoryRead(**dict(row))


async def list_inventory(
    conn: asyncpg.Connection, offset: int = 0, limit: int = 100
) -> list[InventoryRead]:
    rows = await conn.fetch(
        """
        SELECT inventory_id, product_id, warehouse_id, quantity, reorder_level, last_restocked, created_by, updated_by,
               created_at, updated_at
        FROM inventory
        WHERE deleted = FALSE
        ORDER BY quantity
        LIMIT $1 OFFSET $2
        """,
        limit, offset,
    )
    return [InventoryRead(**dict(r)) for r in rows]


async def update_inventory(
    conn: asyncpg.Connection, inventory_id: str, data: InventoryUpdate, updated_by: Optional[str] = None
) -> Optional[InventoryRead]:
    row = await conn.fetchrow(
        """
        UPDATE inventory
        SET
            product_id = COALESCE($1, product_id),
            warehouse_id = COALESCE($2, warehouse_id),
            quantity = COALESCE($3, quantity),
            reorder_level = COALESCE($4, reorder_level),
            last_restocked = COALESCE($5, last_restocked),
            updated_by = $6,
            updated_at = CURRENT_TIMESTAMP
        WHERE inventory_id = $7 AND deleted = FALSE
        RETURNING inventory_id, product_id, warehouse_id, quantity, reorder_level, last_restocked,
                  created_at, updated_at, created_by, updated_by
        """,
        data.product_id, data.warehouse_id, data.quantity,
        data.reorder_level, data.last_restocked, updated_by, inventory_id,
    )
    return InventoryRead(**dict(row)) if row else None


async def delete_inventory(
    conn: asyncpg.Connection, inventory_id: str, deleted_by: Optional[str] = None
) -> bool:
    result = await conn.execute(
        """
        UPDATE inventory
        SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
        WHERE inventory_id = $1 AND deleted = FALSE
        """,
        inventory_id, deleted_by,
    )
    return result == "UPDATE 1"