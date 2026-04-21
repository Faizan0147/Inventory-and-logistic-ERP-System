from fastapi import HTTPException
import asyncpg

from app.dto.invoice import InvoiceCreate, InvoiceUpdate, InvoiceRead
from app.repositories import invoice_repo


async def create_invoice(
    conn: asyncpg.Connection,
    body: InvoiceCreate,
    current_user: dict) -> InvoiceRead:
    # If the user is a SUPPLIER, ensure they are creating an invoice for themselves
    if current_user["role"] == "SUPPLIER" and body.supplier_id != current_user["supplier_id"]:
         raise HTTPException(status_code=403, detail="Suppliers can only create invoices for themselves")
         
    return await invoice_repo.create_invoice(
        conn, body, created_by=current_user["user_id"])


async def list_invoices(
    conn: asyncpg.Connection, offset: int, limit: int, current_user: dict) -> list[InvoiceRead]:
    supplier_id = current_user["supplier_id"] if current_user["role"] == "SUPPLIER" else None
    return await invoice_repo.list_invoices(conn, offset, limit, supplier_id=supplier_id)


async def get_invoice(
    conn: asyncpg.Connection, invoice_id: str, current_user: dict) -> InvoiceRead:
    supplier_id = current_user["supplier_id"] if current_user["role"] == "SUPPLIER" else None
    invoice = await invoice_repo.get_invoice(conn, invoice_id, supplier_id=supplier_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


async def update_invoice(
    conn: asyncpg.Connection, invoice_id: str, body: InvoiceUpdate, current_user: dict
) -> InvoiceRead:
    supplier_id = current_user["supplier_id"] if current_user["role"] == "SUPPLIER" else None
    
    # If a supplier tries to update and changes the supplier_id, block it
    if current_user["role"] == "SUPPLIER" and body.supplier_id and body.supplier_id != current_user["supplier_id"]:
        raise HTTPException(status_code=403, detail="Cannot change supplier assignment")
        
    invoice = await invoice_repo.update_invoice(conn, invoice_id, body, updated_by=current_user["user_id"], supplier_id=supplier_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found or access denied")
    return invoice


async def delete_invoice(
    conn: asyncpg.Connection, invoice_id: str, current_user: dict) -> None:
    supplier_id = current_user["supplier_id"] if current_user["role"] == "SUPPLIER" else None
    deleted = await invoice_repo.delete_invoice(conn, invoice_id, deleted_by=current_user["user_id"], supplier_id=supplier_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Invoice not found or access denied")