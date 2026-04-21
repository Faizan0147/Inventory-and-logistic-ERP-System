from typing import Annotated

from fastapi import APIRouter, Depends, status
import asyncpg

from app.database import get_connection
from app.utils.dependencies import get_current_user
from app.dto.supplier import SupplierCreate, SupplierUpdate, SupplierRead
from app.controllers import supplier as supplier_controller

router = APIRouter()

Conn = Annotated[asyncpg.Connection, Depends(get_connection)]
CurrentUser = Annotated[dict, Depends(get_current_user)]


@router.post("/", response_model=SupplierRead, status_code=status.HTTP_201_CREATED)
async def create_supplier(body: SupplierCreate, conn: Conn, current_user: CurrentUser):
    return await supplier_controller.create_supplier(conn, body, current_user)


@router.get("/", response_model=list[SupplierRead])
async def list_suppliers(conn: Conn, current_user: CurrentUser, offset: int = 0, limit: int = 100):
    return await supplier_controller.list_suppliers(conn, offset, limit, current_user=current_user)


@router.get("/{supplier_id}", response_model=SupplierRead)
async def get_supplier(supplier_id: str, conn: Conn, current_user: CurrentUser):
    return await supplier_controller.get_supplier(conn, supplier_id, current_user=current_user)



@router.patch("/{supplier_id}", response_model=SupplierRead)
async def update_supplier(supplier_id: str, body: SupplierUpdate, conn: Conn, current_user: CurrentUser):
    return await supplier_controller.update_supplier(conn, supplier_id, body, current_user)


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(supplier_id: str, conn: Conn, current_user: CurrentUser):
    await supplier_controller.delete_supplier(conn, supplier_id, current_user)
