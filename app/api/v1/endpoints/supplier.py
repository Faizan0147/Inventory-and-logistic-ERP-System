from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg

from app.database import get_connection
from app.dto.supplier import (
    SupplierCreate,
    SupplierUpdate,
    SupplierRead,
    SupplierWithBankDetails,
)
from app.repositories import supplier_repo

router = APIRouter()

# Shorthand type for the injected connection
Conn = Annotated[asyncpg.Connection, Depends(get_connection)]


# Supplier Endpoints
@router.post("/", response_model=SupplierRead, status_code=status.HTTP_201_CREATED)
async def create_supplier(body: SupplierCreate, conn: Conn):
    return await supplier_repo.create_supplier(conn, body)


@router.get("/", response_model=list[SupplierRead])
async def list_suppliers(conn: Conn, offset: int = 0, limit: int = 100):
    return await supplier_repo.list_suppliers(conn, offset, limit)


@router.get("/{supplier_id}", response_model=SupplierWithBankDetails)
async def get_supplier(supplier_id: UUID, conn: Conn):
    supplier = await supplier_repo.get_supplier(conn, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.patch("/{supplier_id}", response_model=SupplierRead)
async def update_supplier(supplier_id: UUID, body: SupplierUpdate, conn: Conn):
    supplier = await supplier_repo.update_supplier(conn, supplier_id, body)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(supplier_id: UUID, conn: Conn):
    deleted = await supplier_repo.delete_supplier(conn, supplier_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Supplier not found")
