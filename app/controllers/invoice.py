import logging
from fastapi import HTTPException
import asyncpg

from app.dto.invoice import (
    InvoiceCreate, InvoiceRead, InvoiceUpdate,
)
from app.repositories import invoice_repo

logger = logging.getLogger(__name__)


def _get_current_user(current_user: dict) -> str | None:
    """Return user_id for SUPPLIER (scoped access), None for ADMIN (full access)."""
    return current_user["user_id"] if current_user["role"] == "SUPPLIER" else None


async def create_invoice(
    conn: asyncpg.Connection,
    body: InvoiceCreate,
    current_user: dict,
) -> InvoiceRead:
    try:
        return await invoice_repo.create_invoice(
            conn, body, user_id=current_user["user_id"], created_by=current_user["user_id"]
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except RuntimeError as e:
        logger.error("create_invoice failed for user %s: %s", current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))


async def get_invoice(
    conn: asyncpg.Connection, 
    invoice_id: str, 
    current_user: dict
) -> InvoiceRead:
    try:
        invoice = await invoice_repo.get_invoice(
            conn, invoice_id, user_id=_get_current_user(current_user)
        )
    except RuntimeError as e:
        logger.error("get_invoice(%s) failed for user %s: %s", invoice_id, current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


async def list_invoices(
    conn: asyncpg.Connection, 
    offset: int, 
    limit: int, 
    current_user: dict
) -> list[InvoiceRead]:
    try:
        return await invoice_repo.list_invoices(
            conn, offset, limit, user_id=_get_current_user(current_user)
        )
    except RuntimeError as e:
        logger.error("list_invoices failed for user %s: %s", current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))


async def update_invoice(
    conn: asyncpg.Connection, 
    invoice_id: str, 
    body: InvoiceUpdate, 
    current_user: dict
) -> InvoiceRead:
    try:
        invoice = await invoice_repo.update_invoice(
            conn, invoice_id, body, 
            updated_by=current_user["user_id"], 
            user_id=_get_current_user(current_user)
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except RuntimeError as e:
        logger.error("update_invoice(%s) failed for user %s: %s", invoice_id, current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


async def delete_invoice(
    conn: asyncpg.Connection, 
    invoice_id: str, 
    current_user: dict
) -> dict:
    try:
        deleted = await invoice_repo.delete_invoice(
            conn, invoice_id, 
            deleted_by=current_user["user_id"], 
            user_id=_get_current_user(current_user)
        )
    except RuntimeError as e:
        logger.error("delete_invoice(%s) failed for user %s: %s", invoice_id, current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))

    if not deleted:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return {"message": "Invoice deleted successfully"}
