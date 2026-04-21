from uuid import uuid4
from typing import Optional
import asyncpg

from app.dto.invoice import (
    InvoiceCreate, InvoiceRead, InvoiceUpdate,
)


async def create_invoice(
    conn: asyncpg.Connection, data: InvoiceCreate, created_by: Optional[str] = None
) -> InvoiceRead:
    row = await conn.fetchrow(
        """
        INSERT INTO invoices (invoice_id, supplier_id, po_id, invoice_number, invoice_date, total_amount, status, created_by, updated_by)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $8)
        RETURNING invoice_id, supplier_id, po_id, invoice_number, invoice_date,
                  total_amount, status, created_at, updated_at, created_by, updated_by
        """,
        str(uuid4()), data.supplier_id, data.po_id, data.invoice_number,
        data.invoice_date, data.total_amount, data.status, created_by,
    )
    return InvoiceRead(**dict(row))


async def get_invoice(conn: asyncpg.Connection, invoice_id: str, supplier_id: Optional[str] = None) -> Optional[InvoiceRead]:
    query = """
        SELECT invoice_id, supplier_id, po_id, invoice_number, invoice_date,
               total_amount, status, created_at, updated_at, created_by, updated_by
        FROM invoices
        WHERE invoice_id = $1 AND deleted = FALSE
    """
    params = [invoice_id]
    if supplier_id:
        query += " AND supplier_id = $2"
        params.append(supplier_id)
        
    row = await conn.fetchrow(query, *params)
    if not row:
        return None
    return InvoiceRead(**dict(row))


async def list_invoices(
    conn: asyncpg.Connection, offset: int = 0, limit: int = 100, supplier_id: Optional[str] = None
) -> list[InvoiceRead]:
    query = """
        SELECT invoice_id, supplier_id, po_id, invoice_number, invoice_date,
               total_amount, status, created_at, updated_at, created_by, updated_by
        FROM invoices
        WHERE deleted = FALSE
    """
    params = [limit, offset]
    if supplier_id:
        query += " AND supplier_id = $3"
        params.append(supplier_id)
        
    query += " ORDER BY invoice_date DESC LIMIT $1 OFFSET $2"
    
    rows = await conn.fetch(query, *params)
    return [InvoiceRead(**dict(r)) for r in rows]


async def update_invoice(
    conn: asyncpg.Connection, invoice_id: str, data: InvoiceUpdate, updated_by: Optional[str] = None, supplier_id: Optional[str] = None
) -> Optional[InvoiceRead]:
    query = """
        UPDATE invoices
        SET
            supplier_id = COALESCE($1, supplier_id),
            po_id = COALESCE($2, po_id),
            invoice_number = COALESCE($3, invoice_number),
            invoice_date = COALESCE($4, invoice_date),
            total_amount = COALESCE($5, total_amount),
            status = COALESCE($6, status),
            updated_by = $7,
            updated_at = CURRENT_TIMESTAMP
        WHERE invoice_id = $8 AND deleted = FALSE
    """
    params = [
        data.supplier_id, data.po_id, data.invoice_number, data.invoice_date,
        data.total_amount, data.status, updated_by, invoice_id
    ]
    if supplier_id:
        query = query.replace("WHERE invoice_id = $8", "WHERE invoice_id = $8 AND supplier_id = $9")
        params.append(supplier_id)

    query += " RETURNING invoice_id, supplier_id, po_id, invoice_number, invoice_date, total_amount, status, created_at, updated_at, created_by, updated_by"
    
    row = await conn.fetchrow(query, *params)
    return InvoiceRead(**dict(row)) if row else None


async def delete_invoice(
    conn: asyncpg.Connection, invoice_id: str, deleted_by: Optional[str] = None, supplier_id: Optional[str] = None
) -> bool:
    query = """
        UPDATE invoices
        SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
        WHERE invoice_id = $1 AND deleted = FALSE
    """
    params = [invoice_id, deleted_by]
    if supplier_id:
        query += " AND supplier_id = $3"
        params.append(supplier_id)
        
    result = await conn.execute(query, *params)
    return result == "UPDATE 1"