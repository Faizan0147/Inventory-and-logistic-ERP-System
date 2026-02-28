from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg

from app.database import get_connection
from app.dto.supplierbankdetails import (
    SupplierBankDetailsCreate,
    SupplierBankDetailsRead,
)
from app.repositories import supplier_repo

router = APIRouter()

# Shorthand type for the injected connection
Conn = Annotated[asyncpg.Connection, Depends(get_connection)]


# Bank Details
@router.post("/{supplier_id}/bank-details", response_model=SupplierBankDetailsRead, status_code=status.HTTP_201_CREATED)
async def add_bank_details(supplier_id: UUID, body: SupplierBankDetailsCreate, conn: Conn):
    supplier = await supplier_repo.get_supplier(conn, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return await supplier_repo.add_bank_details(conn, supplier_id, body)


@router.delete("/{supplier_id}/bank-details/{bank_detail_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bank_details(supplier_id: UUID, bank_detail_id: UUID, conn: Conn):
    deleted = await supplier_repo.delete_bank_details(conn, bank_detail_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Bank detail not found")
