import logging
from uuid import uuid4
from typing import Optional
import asyncpg

from app.dto.invoice import (
    InvoiceCreate,
    InvoiceRead,
    InvoiceUpdate,
    SupplierSummary,
    PurchaseOrderSummary,
)

logger = logging.getLogger(__name__)

_SELECT = """
    SELECT
        i.invoice_id, i.supplier_id, i.user_id, i.po_id,
        i.invoice_number, i.invoice_date, i.total_amount, i.status,
        i.created_at, i.updated_at, i.created_by, i.updated_by,
        s.supplier_name, s.contact_email, s.contact_phone,
        po.order_number, po.order_date, po.status AS po_status
    FROM invoices i
    LEFT JOIN suppliers s ON s.supplier_id = i.supplier_id AND s.deleted = FALSE
    LEFT JOIN purchase_orders po ON po.po_id = i.po_id AND po.deleted = FALSE
"""


def _build(row: asyncpg.Record) -> InvoiceRead:
    d = dict(row)
    supplier = None
    if d.get("supplier_name"):
        supplier = SupplierSummary(
            supplier_id=d["supplier_id"],
            supplier_name=d["supplier_name"],
            contact_email=d.get("contact_email"),
            contact_phone=d.get("contact_phone"),
        )
    purchase_order = None
    if d.get("po_id") and (d.get("order_number") is not None or d.get("order_date") is not None):
        purchase_order = PurchaseOrderSummary(
            po_id=d["po_id"],
            order_number=d.get("order_number"),
            order_date=d.get("order_date"),
            status=d.get("po_status"),
        )
    return InvoiceRead(
        invoice_id=d["invoice_id"],
        supplier_id=d["supplier_id"],
        user_id=d["user_id"],
        po_id=d.get("po_id"),
        invoice_number=d.get("invoice_number"),
        invoice_date=d.get("invoice_date"),
        total_amount=d.get("total_amount"),
        status=d.get("status"),
        supplier=supplier,
        purchase_order=purchase_order,
        created_at=d.get("created_at"),
        updated_at=d.get("updated_at"),
        created_by=d.get("created_by"),
        updated_by=d.get("updated_by"),
    )


async def create_invoice(
    conn: asyncpg.Connection,
    data: InvoiceCreate,
    user_id: str,
    created_by: Optional[str] = None,
) -> InvoiceRead:
    try:
        row = await conn.fetchrow(
            """
            INSERT INTO invoices (
                invoice_id, supplier_id, po_id, invoice_number, invoice_date,
                total_amount, status, user_id, created_by, updated_by
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $9)
            RETURNING invoice_id
            """,
            str(uuid4()), data.supplier_id, data.po_id, data.invoice_number,
            data.invoice_date, data.total_amount, data.status, user_id, created_by,
        )
        return await get_invoice(conn, row["invoice_id"])

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
    user_id: Optional[str] = None,
) -> Optional[InvoiceRead]:
    try:
        query = _SELECT + " WHERE i.invoice_id = $1 AND i.deleted = FALSE"
        params = [invoice_id]
        if user_id:
            query += " AND i.user_id = $2"
            params.append(user_id)
        row = await conn.fetchrow(query, *params)
        return _build(row) if row else None
    except asyncpg.PostgresError as e:
        logger.error("get_invoice(%s): database error — %s", invoice_id, e)
        raise RuntimeError(f"Database error while fetching invoice: {e}")


async def list_invoices(
    conn: asyncpg.Connection,
    offset: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
) -> list[InvoiceRead]:
    try:
        query = _SELECT + " WHERE i.deleted = FALSE"
        params = [limit, offset]
        if user_id:
            query += " AND i.user_id = $3"
            params.append(user_id)
        query += " ORDER BY i.invoice_date DESC LIMIT $1 OFFSET $2"
        rows = await conn.fetch(query, *params)
        return [_build(r) for r in rows]
    except asyncpg.PostgresError as e:
        logger.error("list_invoices: database error — %s", e)
        raise RuntimeError(f"Database error while listing invoices: {e}")


async def update_invoice(
    conn: asyncpg.Connection,
    invoice_id: str,
    data: InvoiceUpdate,
    updated_by: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Optional[InvoiceRead]:
    try:
        query = """
            UPDATE invoices
            SET
                supplier_id    = COALESCE($1, supplier_id),
                po_id          = COALESCE($2, po_id),
                invoice_number = COALESCE($3, invoice_number),
                invoice_date   = COALESCE($4, invoice_date),
                total_amount   = COALESCE($5, total_amount),
                status         = COALESCE($6, status),
                updated_by     = $7,
                updated_at     = CURRENT_TIMESTAMP
            WHERE invoice_id = $8 AND deleted = FALSE
        """
        params = [
            data.supplier_id, data.po_id, data.invoice_number,
            data.invoice_date, data.total_amount, data.status, updated_by, invoice_id,
        ]
        if user_id:
            query += " AND user_id = $9"
            params.append(user_id)
        query += " RETURNING invoice_id"
        row = await conn.fetchrow(query, *params)
        if not row:
            return None
        return await get_invoice(conn, row["invoice_id"])

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
    user_id: Optional[str] = None,
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
