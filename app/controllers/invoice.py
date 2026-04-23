from fastapi import HTTPException
import asyncpg

from app.dto.invoice import InvoiceCreate, InvoiceUpdate, InvoiceRead
from app.repositories import invoice_repo


async def create_invoice(
    conn: asyncpg.Connection,
    body: InvoiceCreate,
    current_user: dict) -> InvoiceRead:
    return await invoice_repo.create_invoice(
        conn, body, created_by=current_user["user_id"])


async def list_invoices(
    conn: asyncpg.Connection, offset: int, limit: int) -> list[InvoiceRead]:
    return await invoice_repo.list_invoices(conn, offset, limit)


async def get_invoice(
    conn: asyncpg.Connection, invoice_id: str) -> InvoiceRead:
    invoice = await invoice_repo.get_invoice(conn, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


async def update_invoice(
    conn: asyncpg.Connection, invoice_id: str, body: InvoiceUpdate, current_user: dict
) -> InvoiceRead:
    invoice = await invoice_repo.update_invoice(conn, invoice_id, body, updated_by=current_user["user_id"])
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


async def delete_invoice(
    conn: asyncpg.Connection, invoice_id: str, current_user: dict) -> None:
    deleted = await invoice_repo.delete_invoice(conn, invoice_id, deleted_by=current_user["user_id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Invoice not found")