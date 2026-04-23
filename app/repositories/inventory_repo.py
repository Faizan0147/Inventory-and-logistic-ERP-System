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
        INSERT INTO inventory (inventory_id, product_id, warehouse_id, quantity, reorder_level, last_restocked, user_id, created_by, updated_by)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $7, $7)
        RETURNING inventory_id, product_id, warehouse_id, quantity, reorder_level, last_restocked,
                  user_id, created_at, updated_at, created_by, updated_by
        """,
        str(uuid4()), data.product_id, data.warehouse_id,
        data.quantity, data.reorder_level, data.last_restocked, created_by,
    )
    return InventoryRead(**dict(row))


async def get_inventory(
    conn: asyncpg.Connection, inventory_id: str, user_id: Optional[str] = None
) -> Optional[InventoryRead]:
    query = """
        SELECT inventory_id, product_id, warehouse_id, quantity, reorder_level, last_restocked,
               user_id, created_at, updated_at, created_by, updated_by
        FROM inventory
        WHERE inventory_id = $1 AND deleted = FALSE
    """
    params = [inventory_id]
    if user_id:
        query += " AND user_id = $2"
        params.append(user_id)

    row = await conn.fetchrow(query, *params)
    return InventoryRead(**dict(row)) if row else None


async def list_inventory(
    conn: asyncpg.Connection, offset: int = 0, limit: int = 100, user_id: Optional[str] = None
) -> list[InventoryRead]:
    query = """
        SELECT inventory_id, product_id, warehouse_id, quantity, reorder_level, last_restocked,
               user_id, created_at, updated_at, created_by, updated_by
        FROM inventory
        WHERE deleted = FALSE
    """
    params = [limit, offset]
    if user_id:
        query += " AND user_id = $3"
        params.append(user_id)

    query += " ORDER BY quantity LIMIT $1 OFFSET $2"
    rows = await conn.fetch(query, *params)
    return [InventoryRead(**dict(r)) for r in rows]


async def update_inventory(
    conn: asyncpg.Connection, inventory_id: str, data: InventoryUpdate,
    updated_by: Optional[str] = None, user_id: Optional[str] = None
) -> Optional[InventoryRead]:
    query = """
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
    """
    params = [
        data.product_id, data.warehouse_id, data.quantity,
        data.reorder_level, data.last_restocked, updated_by, inventory_id
    ]
    if user_id:
        query += " AND user_id = $8"
        params.append(user_id)

    query += " RETURNING inventory_id, product_id, warehouse_id, quantity, reorder_level, last_restocked, user_id, created_at, updated_at, created_by, updated_by"
    row = await conn.fetchrow(query, *params)
    return InventoryRead(**dict(row)) if row else None


async def delete_inventory(
    conn: asyncpg.Connection, inventory_id: str, deleted_by: Optional[str] = None, user_id: Optional[str] = None
) -> bool:
    query = """
        UPDATE inventory
        SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
        WHERE inventory_id = $1 AND deleted = FALSE
    """
    params = [inventory_id, deleted_by]
    if user_id:
        query += " AND user_id = $3"
        params.append(user_id)

    result = await conn.execute(query, *params)
    return result == "UPDATE 1"
