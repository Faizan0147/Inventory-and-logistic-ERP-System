from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status
import asyncpg

from app.database import get_connection
from app.utils.dependencies import get_current_user
from app.dto.invoice_item import InvoiceItemCreate, InvoiceItemUpdate, InvoiceItemRead
from app.controllers import invoice_item as invoice_item_controller

router = APIRouter()

Conn = Annotated[asyncpg.Connection, Depends(get_connection)]
CurrentUser = Annotated[dict, Depends(get_current_user)]


@router.post("/", response_model=InvoiceItemRead, status_code=status.HTTP_201_CREATED)
async def create_invoice_item(body: InvoiceItemCreate, conn: Conn, current_user: CurrentUser):
    return await invoice_item_controller.create_invoice_item(conn, body, current_user)


@router.get("/", response_model=list[InvoiceItemRead])
async def list_invoice_items(
    conn: Conn,
    current_user: CurrentUser,
    invoice_id: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
):
    return await invoice_item_controller.list_invoice_items(conn, invoice_id, offset, limit)


@router.get("/{invoice_item_id}", response_model=InvoiceItemRead)
async def get_invoice_item(invoice_item_id: str, conn: Conn, current_user: CurrentUser):
    return await invoice_item_controller.get_invoice_item(conn, invoice_item_id)


@router.patch("/{invoice_item_id}", response_model=InvoiceItemRead)
async def update_invoice_item(
    invoice_item_id: str, body: InvoiceItemUpdate, conn: Conn, current_user: CurrentUser
):
    return await invoice_item_controller.update_invoice_item(conn, invoice_item_id, body, current_user)


@router.delete("/{invoice_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice_item(invoice_item_id: str, conn: Conn, current_user: CurrentUser):
    await invoice_item_controller.delete_invoice_item(conn, invoice_item_id, current_user)