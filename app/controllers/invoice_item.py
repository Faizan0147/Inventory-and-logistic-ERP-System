import logging
from fastapi import HTTPException
import asyncpg

from app.dto.invoice_item import InvoiceItemCreate, InvoiceItemUpdate, InvoiceItemRead
from app.repositories import invoice_item_repo

logger = logging.getLogger(__name__)


def _get_current_user(current_user: dict) -> str | None:
    """Return user_id for SUPPLIER (scoped access), None for ADMIN (full access)."""
    return current_user["user_id"] if current_user["role"] == "SUPPLIER" else None


async def create_invoice_item(
    conn: asyncpg.Connection,
    body: InvoiceItemCreate,
    current_user: dict,
) -> InvoiceItemRead:
    try:
        return await invoice_item_repo.create_invoice_item(
            conn, body, user_id=current_user["user_id"], created_by=current_user["user_id"]
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except RuntimeError as e:
        logger.error("create_invoice_item failed for user %s: %s", current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))


async def get_invoice_item(
    conn: asyncpg.Connection, 
    invoice_item_id: str, 
    current_user: dict
) -> InvoiceItemRead:
    try:
        item = await invoice_item_repo.get_invoice_item(
            conn, invoice_item_id, user_id=_get_current_user(current_user)
        )
    except RuntimeError as e:
        logger.error("get_invoice_item(%s) failed for user %s: %s", invoice_item_id, current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))

    if not item:
        raise HTTPException(status_code=404, detail="Invoice item not found")
    return item


async def list_invoice_items(
    conn: asyncpg.Connection,
    invoice_id: str,
    offset: int,
    limit: int,
    current_user: dict,
) -> list[InvoiceItemRead]:
    try:
        return await invoice_item_repo.list_invoice_items(
            conn, invoice_id, offset, limit, user_id=_get_current_user(current_user)
        )
    except RuntimeError as e:
        logger.error("list_invoice_items(%s) failed for user %s: %s", invoice_id, current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))


async def update_invoice_item(
    conn: asyncpg.Connection,
    invoice_item_id: str,
    body: InvoiceItemUpdate,
    current_user: dict,
) -> InvoiceItemRead:
    try:
        item = await invoice_item_repo.update_invoice_item(
            conn, invoice_item_id, body, 
            updated_by=current_user["user_id"], 
            user_id=_get_current_user(current_user)
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except RuntimeError as e:
        logger.error("update_invoice_item(%s) failed for user %s: %s", invoice_item_id, current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))

    if not item:
        raise HTTPException(status_code=404, detail="Invoice item not found or access denied")
    return item


async def delete_invoice_item(
    conn: asyncpg.Connection,
    invoice_item_id: str,
    current_user: dict,
) -> None:
    try:
        deleted = await invoice_item_repo.delete_invoice_item(
            conn, invoice_item_id, 
            deleted_by=current_user["user_id"], 
            user_id=_get_current_user(current_user)
        )
    except RuntimeError as e:
        logger.error("delete_invoice_item(%s) failed for user %s: %s", invoice_item_id, current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))

    if not deleted:
        raise HTTPException(status_code=404, detail="Invoice item not found or access denied")
