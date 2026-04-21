from fastapi import HTTPException
import asyncpg

from app.dto.shipments import ShipmentCreate, ShipmentUpdate, ShipmentRead
from app.repositories import shipments_repo


async def create_shipment(
    conn: asyncpg.Connection,
    data: ShipmentCreate,
    current_user: dict,
) -> ShipmentRead:
    # If the user is a SUPPLIER, ensure they are creating a shipment for themselves
    if current_user["role"] == "SUPPLIER" and data.supplier_id != current_user["supplier_id"]:
         raise HTTPException(status_code=403, detail="Suppliers can only create shipments for themselves")
         
    return await shipments_repo.create_shipment(
        conn, data, created_by=current_user["user_id"]
    )


async def list_shipments(
    conn: asyncpg.Connection, offset: int, limit: int, current_user: dict
) -> list[ShipmentRead]:
    supplier_id = current_user["supplier_id"] if current_user["role"] == "SUPPLIER" else None
    return await shipments_repo.list_shipments(conn, offset, limit, supplier_id=supplier_id)


async def get_shipment(
    conn: asyncpg.Connection, shipment_id: str, current_user: dict
) -> ShipmentRead:
    supplier_id = current_user["supplier_id"] if current_user["role"] == "SUPPLIER" else None
    shipment = await shipments_repo.get_shipment(conn, shipment_id, supplier_id=supplier_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


async def update_shipment(
    conn: asyncpg.Connection,
    shipment_id: str,
    data: ShipmentUpdate,
    current_user: dict,
) -> ShipmentRead:
    supplier_id = current_user["supplier_id"] if current_user["role"] == "SUPPLIER" else None
    
    shipment = await shipments_repo.update_shipment(
        conn, shipment_id, data, updated_by=current_user["user_id"], supplier_id=supplier_id
    )
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found or access denied")
    return shipment


async def delete_shipment(
    conn: asyncpg.Connection, shipment_id: str, current_user: dict
) -> None:
    supplier_id = current_user["supplier_id"] if current_user["role"] == "SUPPLIER" else None
    deleted = await shipments_repo.delete_shipment(
        conn, shipment_id, deleted_by=current_user["user_id"], supplier_id=supplier_id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Shipment not found or access denied")