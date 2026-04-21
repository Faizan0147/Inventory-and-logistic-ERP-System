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


async def get_po_item(conn: asyncpg.Connection, po_item_id: str, supplier_id: Optional[str] = None) -> Optional[POItemRead]:
    query = """
        SELECT poi.po_item_id, poi.po_id, poi.product_id, poi.quantity, poi.price,
               poi.created_at, poi.updated_at, poi.created_by, poi.updated_by
        FROM purchase_order_items poi
        JOIN purchase_orders po ON poi.po_id = po.po_id
        WHERE poi.po_item_id = $1 AND poi.deleted = FALSE
    """
    params = [po_item_id]
    if supplier_id:
        query += " AND po.supplier_id = $2"
        params.append(supplier_id)
        
    row = await conn.fetchrow(query, *params)
    if not row:
        return None
    return POItemRead(**dict(row))


async def list_po_items(
    conn: asyncpg.Connection, po_id: str, supplier_id: Optional[str] = None
) -> list[POItemRead]:
    query = """
        SELECT poi.po_item_id, poi.po_id, poi.product_id, poi.quantity, poi.price,
               poi.created_at, poi.updated_at, poi.created_by, poi.updated_by
        FROM purchase_order_items poi
        JOIN purchase_orders po ON poi.po_id = po.po_id
        WHERE poi.po_id = $1 AND poi.deleted = FALSE
    """
    params = [po_id]
    if supplier_id:
        query += " AND po.supplier_id = $2"
        params.append(supplier_id)
        
    rows = await conn.fetch(query, *params)
    return [POItemRead(**dict(r)) for r in rows]


async def update_po_item(
    conn: asyncpg.Connection, po_item_id: str, data: POItemUpdate, updated_by: Optional[str] = None, supplier_id: Optional[str] = None
) -> Optional[POItemRead]:
    # We join with purchase_orders in the WHERE clause of the UPDATE (using subquery for safety in asyncpg)
    query = """
        UPDATE purchase_order_items poi
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
    
    if supplier_id:
        query += " AND po_id IN (SELECT po_id FROM purchase_orders WHERE supplier_id = $7)"
        params.append(supplier_id)
        
    query += " RETURNING po_item_id, po_id, product_id, quantity, price, created_at, updated_at, created_by, updated_by"
    
    row = await conn.fetchrow(query, *params)
    return POItemRead(**dict(row)) if row else None


async def delete_po_item(
    conn: asyncpg.Connection, po_item_id: str, deleted_by: Optional[str] = None, supplier_id: Optional[str] = None
) -> bool:
    query = """
        UPDATE purchase_order_items
        SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
        WHERE po_item_id = $1 AND deleted = FALSE
    """
    params = [po_item_id, deleted_by]
    
    if supplier_id:
        query += " AND po_id IN (SELECT po_id FROM purchase_orders WHERE supplier_id = $3)"
        params.append(supplier_id)
        
    result = await conn.execute(query, *params)
    return result == "UPDATE 1"