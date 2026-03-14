from typing import Optional
import asyncpg
from uuid import uuid4
from app.dto.poi import POItemCreate, POItemRead, POItemUpdate

async def create_po_item(
    conn: asyncpg.Connection, data: POItemCreate, created_by: Optional[str] = None
) -> POItemRead:
    row = await conn.fetchrow(
        """
        INSERT INTO purchase_order_items (po_item_id, po_id, product_id, quantity, price, created_by, updated_by)
        VALUES ($1, $2, $3, $4, $5, $6, $6)
        RETURNING po_item_id, po_id, product_id, quantity, price,
                  created_at, updated_at, created_by, updated_by
        """,
        str(uuid4()), data.po_id, data.product_id, data.quantity, data.price, created_by,
    )
    return POItemRead(**dict(row))


async def get_po_item(conn: asyncpg.Connection, po_item_id: str) -> Optional[POItemRead]:
    row = await conn.fetchrow(
        """
        SELECT po_item_id, po_id, product_id, quantity, price,
               created_at, updated_at, created_by, updated_by
        FROM purchase_order_items
        WHERE po_item_id = $1 AND deleted = FALSE
        """,
        po_item_id,
    )
    if not row:
        return None
    return POItemRead(**dict(row))


async def list_po_items(
    conn: asyncpg.Connection, po_id: str
) -> list[POItemRead]:
    rows = await conn.fetch(
        """
        SELECT po_item_id, po_id, product_id, quantity, price,
               created_at, updated_at, created_by, updated_by
        FROM purchase_order_items
        WHERE po_id = $1 AND deleted = FALSE
        """,
        po_id,
    )
    return [POItemRead(**dict(r)) for r in rows]


async def update_po_item(
    conn: asyncpg.Connection, po_item_id: str, data: POItemUpdate, updated_by: Optional[str] = None
) -> Optional[POItemRead]:
    row = await conn.fetchrow(
        """
        UPDATE purchase_order_items
        SET
            po_id = COALESCE($1, po_id),
            product_id = COALESCE($2, product_id),
            quantity = COALESCE($3, quantity),
            price = COALESCE($4, price),
            updated_by = $5,
            updated_at = CURRENT_TIMESTAMP
        WHERE po_item_id = $6 AND deleted = FALSE
        RETURNING po_item_id, po_id, product_id, quantity, price,
                  created_at, updated_at, created_by, updated_by
        """,
        data.po_id, data.product_id, data.quantity, data.price, updated_by, po_item_id,
    )
    return POItemRead(**dict(row)) if row else None


async def delete_po_item(
    conn: asyncpg.Connection, po_item_id: str, deleted_by: Optional[str] = None
) -> bool:
    result = await conn.execute(
        """
        UPDATE purchase_order_items
        SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
        WHERE po_item_id = $1 AND deleted = FALSE
        """,
        po_item_id, deleted_by,
    )
    return result == "UPDATE 1"