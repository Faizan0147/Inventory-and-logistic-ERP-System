from fastapi import HTTPException
import asyncpg

from app.dto.shipments import ShipmentCreate, ShipmentUpdate, ShipmentRead
from app.repositories import shipments_repo


async def create_shipment(
    conn: asyncpg.Connection,
    data: ShipmentCreate,
    current_user: dict,
) -> ShipmentRead:
    return await shipments_repo.create_shipment(
        conn, data, created_by=current_user["user_id"]
    )


async def list_shipments(
    conn: asyncpg.Connection, offset: int, limit: int, current_user: dict
) -> list[ShipmentRead]:
    user_id = current_user["user_id"] if current_user["role"] == "SUPPLIER" else None
    return await shipments_repo.list_shipments(conn, offset, limit, user_id=user_id)


async def get_shipment(
    conn: asyncpg.Connection, shipment_id: str, current_user: dict
) -> ShipmentRead:
    user_id = current_user["user_id"] if current_user["role"] == "SUPPLIER" else None
    shipment = await shipments_repo.get_shipment(conn, shipment_id, user_id=user_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


async def update_shipment(
    conn: asyncpg.Connection,
    shipment_id: str,
    data: ShipmentUpdate,
    current_user: dict,
) -> ShipmentRead:
    user_id = current_user["user_id"] if current_user["role"] == "SUPPLIER" else None
    shipment = await shipments_repo.update_shipment(
        conn, shipment_id, data, updated_by=current_user["user_id"], user_id=user_id
    )
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found or access denied")
    return shipment


async def delete_shipment(
    conn: asyncpg.Connection, shipment_id: str, current_user: dict
) -> None:
    user_id = current_user["user_id"] if current_user["role"] == "SUPPLIER" else None
    deleted = await shipments_repo.delete_shipment(
        conn, shipment_id, deleted_by=current_user["user_id"], user_id=user_id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Shipment not found or access denied")
