from typing import Annotated

from fastapi import APIRouter, Depends, status
import asyncpg

from app.database import get_connection
from app.utils.dependencies import get_current_user
from app.dto.invoice import InvoiceCreate, InvoiceRead, InvoiceUpdate
from app.controllers import invoice

router = APIRouter()

Conn = Annotated[asyncpg.Connection, Depends(get_connection)]
CurrentUser = Annotated[dict, Depends(get_current_user)]


router = APIRouter()

@router.post("/", response_model=InvoiceRead, status_code=status.HTTP_201_CREATED)
async def create_invoice(body: InvoiceCreate, conn: Conn, current_user: CurrentUser):
    return await invoice.create_invoice(conn, body, current_user)


@router.get("/", response_model=list[InvoiceRead])
async def list_invoices(conn: Conn, current_user: CurrentUser, offset: int = 0, limit: int = 100):
    return await invoice.list_invoices(conn, offset, limit, current_user=current_user)


@router.get("/{invoice_id}", response_model=InvoiceRead)
async def get_invoice(invoice_id: str, conn: Conn, current_user: CurrentUser):
    return await invoice.get_invoice(conn, invoice_id, current_user=current_user)



@router.put("/{invoice_id}", response_model=InvoiceRead)
async def update_invoice(invoice_id: str, body: InvoiceUpdate, conn: Conn, current_user: CurrentUser):
    return await invoice.update_invoice(conn, invoice_id, body, current_user)


@router.delete("/{invoice_id}", status_code=200)
async def delete_invoice(invoice_id: str, conn: Conn, current_user: CurrentUser) -> dict:
    return await invoice.delete_invoice(conn, invoice_id, current_user)
