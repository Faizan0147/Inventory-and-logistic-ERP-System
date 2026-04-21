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
        INSERT INTO inventory (inventory_id, product_id, warehouse_id, quantity, reorder_level, last_restocked, supplier_id, created_by, updated_by)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $8)
        RETURNING inventory_id, product_id, warehouse_id, quantity, reorder_level, last_restocked, supplier_id,
                  created_at, updated_at, created_by, updated_by
        """,
        str(uuid4()), data.product_id, data.warehouse_id,
        data.quantity, data.reorder_level, data.last_restocked, data.supplier_id, created_by,
    )
    return InventoryRead(**dict(row))


async def get_inventory(conn: asyncpg.Connection, inventory_id: str, supplier_id: Optional[str] = None) -> Optional[InventoryRead]:
    query = """
        SELECT inventory_id, product_id, warehouse_id, quantity, reorder_level, last_restocked, supplier_id,
               created_at, updated_at, created_by, updated_by
        FROM inventory
        WHERE inventory_id = $1 AND deleted = FALSE
    """
    params = [inventory_id]
    if supplier_id:
        query += " AND supplier_id = $2"
        params.append(supplier_id)
        
    row = await conn.fetchrow(query, *params)
    if not row:
        return None
    return InventoryRead(**dict(row))


async def list_inventory(
    conn: asyncpg.Connection, offset: int = 0, limit: int = 100, supplier_id: Optional[str] = None
) -> list[InventoryRead]:
    query = """
        SELECT inventory_id, product_id, warehouse_id, quantity, reorder_level, last_restocked, supplier_id,
               created_at, updated_at, created_by, updated_by
        FROM inventory
        WHERE deleted = FALSE
    """
    params = [limit, offset]
    if supplier_id:
        query += " AND supplier_id = $3"
        params.append(supplier_id)
        
    query += " ORDER BY quantity LIMIT $1 OFFSET $2"
    
    rows = await conn.fetch(query, *params)
    return [InventoryRead(**dict(r)) for r in rows]


async def update_inventory(
    conn: asyncpg.Connection, inventory_id: str, data: InventoryUpdate, updated_by: Optional[str] = None, supplier_id: Optional[str] = None
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
    if supplier_id:
        query = query.replace("WHERE inventory_id = $7", "WHERE inventory_id = $7 AND supplier_id = $8")
        params.append(supplier_id)
        
    query += " RETURNING inventory_id, product_id, warehouse_id, quantity, reorder_level, last_restocked, supplier_id, created_at, updated_at, created_by, updated_by"
    
    row = await conn.fetchrow(query, *params)
    return InventoryRead(**dict(row)) if row else None


async def delete_inventory(
    conn: asyncpg.Connection, inventory_id: str, deleted_by: Optional[str] = None, supplier_id: Optional[str] = None
) -> bool:
    query = """
        UPDATE inventory
        SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
        WHERE inventory_id = $1 AND deleted = FALSE
    """
    params = [inventory_id, deleted_by]
    if supplier_id:
        query += " AND supplier_id = $3"
        params.append(supplier_id)
        
    result = await conn.execute(query, *params)
    return result == "UPDATE 1"