import logging
from uuid import uuid4
from typing import Optional
import asyncpg

from app.dto.inventory import (
    InventoryCreate,
    InventoryRead,
    InventoryUpdate,
)

logger = logging.getLogger(__name__)


async def create_inventory(
    conn: asyncpg.Connection,
    data: InventoryCreate,
    user_id: str,
    created_by: Optional[str] = None,
) -> InventoryRead:

    try:
        row = await conn.fetchrow(
            """
            INSERT INTO inventory (
                inventory_id, user_id, product_id, warehouse_id,
                quantity, reorder_level, last_restocked, created_by, updated_by
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $8)
            RETURNING inventory_id, user_id, product_id, warehouse_id, quantity,
                      reorder_level, last_restocked,
                      created_at, updated_at, created_by, updated_by
            """,
            str(uuid4()),
            user_id,
            data.product_id,
            data.warehouse_id,
            data.quantity,
            data.reorder_level,
            data.last_restocked,
            created_by,
        )
        return InventoryRead(**dict(row))

    except asyncpg.UniqueViolationError:
        logger.warning(
            "create_inventory: duplicate (product_id=%s, warehouse_id=%s)",
            data.product_id, data.warehouse_id,
        )
        raise ValueError("An inventory record for this product and warehouse already exists.")

    except asyncpg.ForeignKeyViolationError as e:
        logger.warning("create_inventory: foreign key violation — %s", e)
        raise ValueError("Invalid product_id or warehouse_id.")

    except asyncpg.PostgresError as e:
        logger.error("create_inventory: database error — %s", e)
        raise RuntimeError(f"Database error while creating inventory: {e}")


async def get_inventory(
    conn: asyncpg.Connection,
    inventory_id: str,
    user_id: Optional[str] = None,
) -> Optional[InventoryRead]:

    try:
        query = """
            SELECT inventory_id, user_id, product_id, warehouse_id, quantity,
                   reorder_level, last_restocked,
                   created_at, updated_at, created_by, updated_by
            FROM inventory
            WHERE inventory_id = $1 AND deleted = FALSE
        """
        params = [inventory_id]
        if user_id:
            query += " AND user_id = $2"
            params.append(user_id)

        row = await conn.fetchrow(query, *params)
        return InventoryRead(**dict(row)) if row else None

    except asyncpg.PostgresError as e:
        logger.error("get_inventory(%s): database error — %s", inventory_id, e)
        raise RuntimeError(f"Database error while fetching inventory: {e}")


async def list_inventory(
    conn: asyncpg.Connection,
    offset: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
) -> list[InventoryRead]:

    try:
        query = """
            SELECT inventory_id, user_id, product_id, warehouse_id, quantity,
                   reorder_level, last_restocked,
                   created_at, updated_at, created_by, updated_by
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

    except asyncpg.PostgresError as e:
        logger.error("list_inventory: database error — %s", e)
        raise RuntimeError(f"Database error while listing inventory: {e}")


async def update_inventory(
    conn: asyncpg.Connection,
    inventory_id: str,
    data: InventoryUpdate,
    updated_by: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Optional[InventoryRead]:

    try:
        query = """
            UPDATE inventory
            SET
                product_id    = COALESCE($1, product_id),
                warehouse_id  = COALESCE($2, warehouse_id),
                quantity      = COALESCE($3, quantity),
                reorder_level = COALESCE($4, reorder_level),
                last_restocked = COALESCE($5, last_restocked),
                updated_by    = $6,
                updated_at    = CURRENT_TIMESTAMP
            WHERE inventory_id = $7 AND deleted = FALSE
        """
        params = [
            data.product_id,
            data.warehouse_id,
            data.quantity,
            data.reorder_level,
            data.last_restocked,
            updated_by,
            inventory_id,
        ]
        if user_id:
            query += " AND user_id = $8"
            params.append(user_id)

        query += """
            RETURNING inventory_id, user_id, product_id, warehouse_id, quantity,
                      reorder_level, last_restocked,
                      created_at, updated_at, created_by, updated_by
        """
        row = await conn.fetchrow(query, *params)
        return InventoryRead(**dict(row)) if row else None

    except asyncpg.UniqueViolationError:
        logger.warning(
            "update_inventory(%s): duplicate (product_id=%s, warehouse_id=%s)",
            inventory_id, data.product_id, data.warehouse_id,
        )
        raise ValueError("An inventory record for this product and warehouse already exists.")

    except asyncpg.ForeignKeyViolationError as e:
        logger.warning("update_inventory(%s): foreign key violation — %s", inventory_id, e)
        raise ValueError("Invalid product_id or warehouse_id.")

    except asyncpg.PostgresError as e:
        logger.error("update_inventory(%s): database error — %s", inventory_id, e)
        raise RuntimeError(f"Database error while updating inventory: {e}")


async def delete_inventory(
    conn: asyncpg.Connection,
    inventory_id: str,
    deleted_by: Optional[str] = None,
    user_id: Optional[str] = None,
) -> bool:

    try:
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

    except asyncpg.PostgresError as e:
        logger.error("delete_inventory(%s): database error — %s", inventory_id, e)
        raise RuntimeError(f"Database error while deleting inventory: {e}")
