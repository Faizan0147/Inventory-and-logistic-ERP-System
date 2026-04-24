import logging
from uuid import uuid4
from typing import Optional
import asyncpg

from app.dto.invoice import (
    InvoiceCreate, InvoiceRead, InvoiceUpdate,
)

logger = logging.getLogger(__name__)


async def create_invoice(
    conn: asyncpg.Connection, 
    data: InvoiceCreate, 
    user_id: str,
    created_by: Optional[str] = None
) -> InvoiceRead:
    try:
        row = await conn.fetchrow(
            """
            INSERT INTO invoices (
                invoice_id, supplier_id, po_id, invoice_number, invoice_date, 
                total_amount, status, user_id, created_by, updated_by
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING invoice_id, supplier_id, po_id, invoice_number, invoice_date,
                      total_amount, status, user_id, created_at, updated_at, created_by, updated_by
            """,
            str(uuid4()), 
            data.supplier_id, 
            data.po_id, 
            data.invoice_number,
            data.invoice_date, 
            data.total_amount, 
            data.status, 
            user_id,
            created_by,
            created_by,
        )
        return InvoiceRead(**dict(row))

    except asyncpg.UniqueViolationError:
        logger.warning("create_invoice: duplicate invoice_number '%s'", data.invoice_number)
        raise ValueError(f"An invoice with number '{data.invoice_number}' already exists.")

    except asyncpg.ForeignKeyViolationError as e:
        logger.warning("create_invoice: foreign key violation — %s", e)
        raise ValueError("Invalid supplier_id or po_id.")

    except asyncpg.PostgresError as e:
        logger.error("create_invoice: database error — %s", e)
        raise RuntimeError(f"Database error while creating invoice: {e}")


async def get_invoice(
    conn: asyncpg.Connection, 
    invoice_id: str, 
    user_id: Optional[str] = None
) -> Optional[InvoiceRead]:
    try:
        query = """
            SELECT invoice_id, supplier_id, po_id, invoice_number, invoice_date,
                   total_amount, status, user_id, created_at, updated_at, created_by, updated_by
            FROM invoices
            WHERE invoice_id = $1 AND deleted = FALSE
        """
        params = [invoice_id]
        if user_id:
            query += " AND user_id = $2"
            params.append(user_id)

        row = await conn.fetchrow(query, *params)
        return InvoiceRead(**dict(row)) if row else None

    except asyncpg.PostgresError as e:
        logger.error("get_invoice(%s): database error — %s", invoice_id, e)
        raise RuntimeError(f"Database error while fetching invoice: {e}")


async def list_invoices(
    conn: asyncpg.Connection, 
    offset: int = 0, 
    limit: int = 100, 
    user_id: Optional[str] = None
) -> list[InvoiceRead]:
    try:
        query = """
            SELECT invoice_id, supplier_id, po_id, invoice_number, invoice_date,
                   total_amount, status, user_id, created_at, updated_at, created_by, updated_by
            FROM invoices
            WHERE deleted = FALSE
        """
        params = [limit, offset]
        if user_id:
            query += " AND user_id = $3"
            params.append(user_id)

        query += " ORDER BY invoice_date DESC LIMIT $1 OFFSET $2"
        rows = await conn.fetch(query, *params)
        return [InvoiceRead(**dict(r)) for r in rows]

    except asyncpg.PostgresError as e:
        logger.error("list_invoices: database error — %s", e)
        raise RuntimeError(f"Database error while listing invoices: {e}")


async def update_invoice(
    conn: asyncpg.Connection, 
    invoice_id: str, 
    data: InvoiceUpdate,
    updated_by: Optional[str] = None, 
    user_id: Optional[str] = None
) -> Optional[InvoiceRead]:
    try:
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
        if user_id:
            query += " AND user_id = $9"
            params.append(user_id)

        query += """
            RETURNING invoice_id, supplier_id, po_id, invoice_number, invoice_date, 
                      total_amount, status, user_id, created_at, updated_at, created_by, updated_by
        """
        row = await conn.fetchrow(query, *params)
        return InvoiceRead(**dict(row)) if row else None

    except asyncpg.UniqueViolationError:
        logger.warning("update_invoice(%s): duplicate invoice_number '%s'", invoice_id, data.invoice_number)
        raise ValueError(f"An invoice with number '{data.invoice_number}' already exists.")

    except asyncpg.ForeignKeyViolationError as e:
        logger.warning("update_invoice(%s): foreign key violation — %s", invoice_id, e)
        raise ValueError("Invalid supplier_id or po_id.")

    except asyncpg.PostgresError as e:
        logger.error("update_invoice(%s): database error — %s", invoice_id, e)
        raise RuntimeError(f"Database error while updating invoice: {e}")


async def delete_invoice(
    conn: asyncpg.Connection, 
    invoice_id: str, 
    deleted_by: Optional[str] = None, 
    user_id: Optional[str] = None
) -> bool:
    try:
        query = """
            UPDATE invoices
            SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
            WHERE invoice_id = $1 AND deleted = FALSE
        """
        params = [invoice_id, deleted_by]
        if user_id:
            query += " AND user_id = $3"
            params.append(user_id)

        result = await conn.execute(query, *params)
        return result == "UPDATE 1"

    except asyncpg.PostgresError as e:
        logger.error("delete_invoice(%s): database error — %s", invoice_id, e)
        raise RuntimeError(f"Database error while deleting invoice: {e}")
