from uuid import uuid4
from typing import Optional
import asyncpg

from app.dto.invoice_item import InvoiceItemCreate, InvoiceItemUpdate, InvoiceItemRead


async def create_invoice_item(
    conn: asyncpg.Connection,
    data: InvoiceItemCreate,
    created_by: Optional[str] = None,
) -> InvoiceItemRead:
    row = await conn.fetchrow(
        """
        INSERT INTO invoice_items
            (invoice_item_id, invoice_id, product_id, quantity, price, created_by, updated_by)
        VALUES ($1, $2, $3, $4, $5, $6, $6)
        RETURNING invoice_item_id, invoice_id, product_id, quantity, price,
                  created_at, updated_at, created_by, updated_by
        """,
        str(uuid4()), data.invoice_id, data.product_id,
        data.quantity, data.price, created_by,
    )
    return InvoiceItemRead(**dict(row))


async def get_invoice_item(
    conn: asyncpg.Connection, invoice_item_id: str, supplier_id: Optional[str] = None
) -> Optional[InvoiceItemRead]:
    query = """
        SELECT ii.invoice_item_id, ii.invoice_id, ii.product_id, ii.quantity, ii.price,
               ii.created_at, ii.updated_at, ii.created_by, ii.updated_by
        FROM invoice_items ii
        JOIN invoices i ON ii.invoice_id = i.invoice_id
        WHERE ii.invoice_item_id = $1 AND ii.deleted = FALSE
    """
    params = [invoice_item_id]
    if supplier_id:
        query += " AND i.supplier_id = $2"
        params.append(supplier_id)
        
    row = await conn.fetchrow(query, *params)
    return InvoiceItemRead(**dict(row)) if row else None


async def list_invoice_items(
    conn: asyncpg.Connection,
    invoice_id: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
    supplier_id: Optional[str] = None,
) -> list[InvoiceItemRead]:
    query = """
        SELECT ii.invoice_item_id, ii.invoice_id, ii.product_id, ii.quantity, ii.price,
               ii.created_at, ii.updated_at, ii.created_by, ii.updated_by
        FROM invoice_items ii
        JOIN invoices i ON ii.invoice_id = i.invoice_id
        WHERE ii.deleted = FALSE
    """
    params = [limit, offset]
    
    if invoice_id:
        query += " AND ii.invoice_id = $3"
        params.append(invoice_id)
    
    if supplier_id:
        supplier_param_index = len(params) + 1
        query += f" AND i.supplier_id = ${supplier_param_index}"
        params.append(supplier_id)
        
    query += " ORDER BY ii.created_at LIMIT $1 OFFSET $2"
    
    rows = await conn.fetch(query, *params)
    return [InvoiceItemRead(**dict(r)) for r in rows]


async def update_invoice_item(
    conn: asyncpg.Connection,
    invoice_item_id: str,
    data: InvoiceItemUpdate,
    updated_by: Optional[str] = None,
    supplier_id: Optional[str] = None,
) -> Optional[InvoiceItemRead]:
    query = """
        UPDATE invoice_items
        SET
            quantity   = COALESCE($1, quantity),
            price      = COALESCE($2, price),
            updated_by = $3,
            updated_at = CURRENT_TIMESTAMP
        WHERE invoice_item_id = $4 AND deleted = FALSE
    """
    params = [data.quantity, data.price, updated_by, invoice_item_id]
    
    if supplier_id:
        query += " AND invoice_id IN (SELECT invoice_id FROM invoices WHERE supplier_id = $5)"
        params.append(supplier_id)
        
    query += " RETURNING invoice_item_id, invoice_id, product_id, quantity, price, created_at, updated_at, created_by, updated_by"
    
    row = await conn.fetchrow(query, *params)
    return InvoiceItemRead(**dict(row)) if row else None


async def delete_invoice_item(
    conn: asyncpg.Connection,
    invoice_item_id: str,
    deleted_by: Optional[str] = None,
    supplier_id: Optional[str] = None,
) -> bool:
    query = """
        UPDATE invoice_items
        SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
        WHERE invoice_item_id = $1 AND deleted = FALSE
    """
    params = [invoice_item_id, deleted_by]
    
    if supplier_id:
        query += " AND invoice_id IN (SELECT invoice_id FROM invoices WHERE supplier_id = $3)"
        params.append(supplier_id)
        
    result = await conn.execute(query, *params)
    return result == "UPDATE 1"