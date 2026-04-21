from fastapi import HTTPException
import asyncpg

from app.dto.invoice_item import InvoiceItemCreate, InvoiceItemUpdate, InvoiceItemRead
from app.repositories import invoice_item_repo


async def create_invoice_item(
    conn: asyncpg.Connection,
    data: InvoiceItemCreate,
    current_user: dict,
) -> InvoiceItemRead:
    # Verify invoice ownership if user is a SUPPLIER
    if current_user["role"] == "SUPPLIER":
        from app.repositories import invoice_repo
        invoice = await invoice_repo.get_invoice(conn, data.invoice_id, supplier_id=current_user["supplier_id"])
        if not invoice:
            raise HTTPException(status_code=403, detail="Cannot add items to another supplier's invoice")

    return await invoice_item_repo.create_invoice_item(
        conn, data, created_by=current_user["user_id"]
    )


async def list_invoice_items(
    conn: asyncpg.Connection,
    invoice_id: str | None,
    offset: int,
    limit: int,
    current_user: dict,
) -> list[InvoiceItemRead]:
    supplier_id = current_user["supplier_id"] if current_user["role"] == "SUPPLIER" else None
    return await invoice_item_repo.list_invoice_items(conn, invoice_id, offset, limit, supplier_id=supplier_id)


async def get_invoice_item(
    conn: asyncpg.Connection, invoice_item_id: str, current_user: dict
) -> InvoiceItemRead:
    supplier_id = current_user["supplier_id"] if current_user["role"] == "SUPPLIER" else None
    item = await invoice_item_repo.get_invoice_item(conn, invoice_item_id, supplier_id=supplier_id)
    if not item:
        raise HTTPException(status_code=404, detail="Invoice item not found")
    return item


async def update_invoice_item(
    conn: asyncpg.Connection,
    invoice_item_id: str,
    data: InvoiceItemUpdate,
    current_user: dict,
) -> InvoiceItemRead:
    supplier_id = current_user["supplier_id"] if current_user["role"] == "SUPPLIER" else None
    item = await invoice_item_repo.update_invoice_item(
        conn, invoice_item_id, data, updated_by=current_user["user_id"], supplier_id=supplier_id
    )
    if not item:
        raise HTTPException(status_code=404, detail="Invoice item not found or access denied")
    return item


async def delete_invoice_item(
    conn: asyncpg.Connection, invoice_item_id: str, current_user: dict
) -> None:
    supplier_id = current_user["supplier_id"] if current_user["role"] == "SUPPLIER" else None
    deleted = await invoice_item_repo.delete_invoice_item(
        conn, invoice_item_id, deleted_by=current_user["user_id"], supplier_id=supplier_id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Invoice item not found or access denied")