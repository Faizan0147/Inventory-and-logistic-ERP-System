from typing import Annotated

from fastapi import APIRouter, Depends, status
import asyncpg

from app.database import get_connection
from app.utils.dependencies import get_current_user
from app.dto.purchase_order import PurchaseOrderCreate, PurchaseOrderRead, PurchaseOrderUpdate
from app.controllers import purchase_order as purchase_order_controller

router = APIRouter()

Conn = Annotated[asyncpg.Connection, Depends(get_connection)]
CurrentUser = Annotated[dict, Depends(get_current_user)]


@router.post("/", response_model=PurchaseOrderRead, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(body: PurchaseOrderCreate, conn: Conn, current_user: CurrentUser):
    return await purchase_order_controller.create_purchase_order(conn, body, current_user)


@router.get("/", response_model=list[PurchaseOrderRead])
async def list_purchase_orders(conn: Conn, current_user: CurrentUser, offset: int = 0, limit: int = 100):
    return await purchase_order_controller.list_purchase_orders(conn, offset, limit, current_user=current_user)


@router.get("/{po_id}", response_model=PurchaseOrderRead)
async def get_purchase_order(po_id: str, conn: Conn, current_user: CurrentUser):
    return await purchase_order_controller.get_purchase_order(conn, po_id, current_user=current_user)



@router.patch("/{po_id}", response_model=PurchaseOrderRead)
async def update_purchase_order(po_id: str, body: PurchaseOrderUpdate, conn: Conn, current_user: CurrentUser):
    return await purchase_order_controller.update_purchase_order(conn, po_id, body, current_user)


@router.delete("/{po_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_purchase_order(po_id: str, conn: Conn, current_user: CurrentUser):
    await purchase_order_controller.delete_purchase_order(conn, po_id, current_user)

