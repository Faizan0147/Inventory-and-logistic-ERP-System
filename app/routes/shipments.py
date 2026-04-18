from typing import Annotated
from fastapi import APIRouter, Depends, status
import asyncpg

from app.database import get_connection
from app.utils.dependencies import get_current_user
from app.dto.shipments import ShipmentCreate, ShipmentUpdate, ShipmentRead
from app.controllers import shipments as shipment_controller

router = APIRouter()

Conn = Annotated[asyncpg.Connection, Depends(get_connection)]
CurrentUser = Annotated[dict, Depends(get_current_user)]


@router.post("/", response_model=ShipmentRead, status_code=status.HTTP_201_CREATED)
async def create_shipment(body: ShipmentCreate, conn: Conn, current_user: CurrentUser):
    return await shipment_controller.create_shipment(conn, body, current_user)


@router.get("/", response_model=list[ShipmentRead])
async def list_shipments(conn: Conn, current_user: CurrentUser, offset: int = 0, limit: int = 100):
    return await shipment_controller.list_shipments(conn, offset, limit)


@router.get("/{shipment_id}", response_model=ShipmentRead)
async def get_shipment(shipment_id: str, conn: Conn, current_user: CurrentUser):
    return await shipment_controller.get_shipment(conn, shipment_id)


@router.patch("/{shipment_id}", response_model=ShipmentRead)
async def update_shipment(shipment_id: str, body: ShipmentUpdate, conn: Conn, current_user: CurrentUser):
    return await shipment_controller.update_shipment(conn, shipment_id, body, current_user)


@router.delete("/{shipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shipment(shipment_id: str, conn: Conn, current_user: CurrentUser):
    await shipment_controller.delete_shipment(conn, shipment_id, current_user)