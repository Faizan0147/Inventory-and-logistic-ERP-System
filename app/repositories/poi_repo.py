import logging
from typing import Optional
import asyncpg
from uuid import uuid4
from app.dto.poi import POItemCreate, POItemRead, POItemUpdate

logger = logging.getLogger(__name__)


async def create_po_item(
    conn: asyncpg.Connection, 
    data: POItemCreate, 
    user_id: str,
    created_by: Optional[str] = None
) -> POItemRead:
    try:
        row = await conn.fetchrow(
            """
            INSERT INTO purchase_order_items (
                po_item_id, po_id, product_id, quantity, price, user_id, created_by, updated_by
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING po_item_id, po_id, product_id, quantity, price,
                      user_id, created_at, updated_at, created_by, updated_by
            """,
            str(uuid4()), 
            data.po_id, 
            data.product_id, 
            data.quantity, 
            data.price, 
            user_id,
            created_by,
            created_by,
        )
        return POItemRead(**dict(row))

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
    user_id: Optional[str] = None
) -> Optional[POItemRead]:
    try:
        query = """
            SELECT po_item_id, po_id, product_id, quantity, price,
                   user_id, created_at, updated_at, created_by, updated_by
            FROM purchase_order_items
            WHERE po_item_id = $1 AND deleted = FALSE
        """
        params = [po_item_id]
        if user_id:
            query += " AND user_id = $2"
            params.append(user_id)

        row = await conn.fetchrow(query, *params)
        return POItemRead(**dict(row)) if row else None

    except asyncpg.PostgresError as e:
        logger.error("get_po_item(%s): database error — %s", po_item_id, e)
        raise RuntimeError(f"Database error while fetching purchase order item: {e}")


async def list_po_items(
    conn: asyncpg.Connection, 
    po_id: str, 
    user_id: Optional[str] = None
) -> list[POItemRead]:
    try:
        query = """
            SELECT po_item_id, po_id, product_id, quantity, price,
                   user_id, created_at, updated_at, created_by, updated_by
            FROM purchase_order_items
            WHERE po_id = $1 AND deleted = FALSE
        """
        params = [po_id]
        if user_id:
            query += " AND user_id = $2"
            params.append(user_id)

        rows = await conn.fetch(query, *params)
        return [POItemRead(**dict(r)) for r in rows]

    except asyncpg.PostgresError as e:
        logger.error("list_po_items(%s): database error — %s", po_id, e)
        raise RuntimeError(f"Database error while listing purchase order items: {e}")


async def update_po_item(
    conn: asyncpg.Connection, 
    po_item_id: str, 
    data: POItemUpdate,
    updated_by: Optional[str] = None, 
    user_id: Optional[str] = None
) -> Optional[POItemRead]:
    try:
        query = """
            UPDATE purchase_order_items
            SET
                po_id = COALESCE($1, po_id),
                product_id = COALESCE($2, product_id),
                quantity = COALESCE($3, quantity),
                price = COALESCE($4, price),
                updated_by = $5,
                updated_at = CURRENT_TIMESTAMP
            WHERE po_item_id = $6 AND deleted = FALSE
        """
        params = [data.po_id, data.product_id, data.quantity, data.price, updated_by, po_item_id]
        if user_id:
            query += " AND user_id = $7"
            params.append(user_id)

        query += """
            RETURNING po_item_id, po_id, product_id, quantity, price, 
                      user_id, created_at, updated_at, created_by, updated_by
        """
        row = await conn.fetchrow(query, *params)
        return POItemRead(**dict(row)) if row else None

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
    user_id: Optional[str] = None
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
