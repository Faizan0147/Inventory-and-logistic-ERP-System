from typing import Annotated

from fastapi import APIRouter, Depends, status
import asyncpg

from app.database import get_connection
from app.utils.dependencies import get_current_user
from app.dto.poi import POItemCreate, POItemRead, POItemUpdate
from app.controllers import poi

router = APIRouter()

Conn = Annotated[asyncpg.Connection, Depends(get_connection)]
CurrentUser = Annotated[dict, Depends(get_current_user)]


@router.post(
    "/{po_id}/items", response_model=POItemRead, status_code=status.HTTP_201_CREATED
)
async def create_po_item(body: POItemCreate, conn: Conn, current_user: CurrentUser):
    return await poi.create_po_item(conn, body, current_user)


@router.get("/{po_id}/items", response_model=list[POItemRead])
async def list_po_items(po_id: str, conn: Conn, current_user: CurrentUser):
    return await poi.list_po_items(conn, po_id, current_user=current_user)


@router.get("/{po_id}/items/{po_item_id}", response_model=POItemRead)
async def get_po_item(po_item_id: str, conn: Conn, current_user: CurrentUser):
    return await poi.get_po_item(conn, po_item_id, current_user=current_user)


@router.put("/{po_id}/items/{po_item_id}", response_model=POItemRead)
async def update_po_item(
    po_item_id: str, body: POItemUpdate, conn: Conn, current_user: CurrentUser
):
    return await poi.update_po_item(conn, po_item_id, body, current_user)


@router.delete("/{po_id}/items/{po_item_id}", status_code=200)
async def delete_po_item(
    po_item_id: str, conn: Conn, current_user: CurrentUser
) -> dict:
    return await poi.delete_po_item(conn, po_item_id, current_user)
