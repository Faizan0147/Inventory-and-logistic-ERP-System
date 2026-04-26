import logging
from fastapi import HTTPException
import asyncpg

from app.dto.shipments import ShipmentCreate, ShipmentUpdate, ShipmentRead
from app.repositories import shipments_repo

logger = logging.getLogger(__name__)


def _get_current_user(current_user: dict) -> str | None:
    return current_user["user_id"] if current_user["role"] == "SUPPLIER" else None


async def create_shipment(
    conn: asyncpg.Connection,
    data: ShipmentCreate,
    current_user: dict,
) -> ShipmentRead:

    try:
        return await shipments_repo.create_shipment(
            conn, data,
            user_id=current_user["user_id"],
            created_by=current_user["user_id"],
        )

    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    except RuntimeError as e:
        logger.error("create_shipment failed for user %s: %s", current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))


async def get_shipment(
    conn: asyncpg.Connection,
    shipment_id: str,
    current_user: dict,
) -> ShipmentRead:

    try:
        shipment = await shipments_repo.get_shipment(
            conn, shipment_id, user_id=_get_current_user(current_user)
        )

    except RuntimeError as e:
        logger.error("get_shipment(%s) failed for user %s: %s", shipment_id, current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))

    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


async def list_shipments(
    conn: asyncpg.Connection,
    offset: int,
    limit: int,
    current_user: dict,
) -> list[ShipmentRead]:

    try:
        return await shipments_repo.list_shipments(
            conn, offset, limit, user_id=_get_current_user(current_user)
        )

    except RuntimeError as e:
        logger.error("list_shipments failed for user %s: %s", current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))


async def update_shipment(
    conn: asyncpg.Connection,
    shipment_id: str,
    data: ShipmentUpdate,
    current_user: dict,
) -> ShipmentRead:

    try:
        shipment = await shipments_repo.update_shipment(
            conn, shipment_id, data,
            updated_by=current_user["user_id"],
            user_id=_get_current_user(current_user),
        )

    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    except RuntimeError as e:
        logger.error("update_shipment(%s) failed for user %s: %s", shipment_id, current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))

    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


async def delete_shipment(
    conn: asyncpg.Connection,
    shipment_id: str,
    current_user: dict,
) -> dict:

    try:
        deleted = await shipments_repo.delete_shipment(
            conn, shipment_id,
            deleted_by=current_user["user_id"],
            user_id=_get_current_user(current_user),
        )
        
    except RuntimeError as e:
        logger.error("delete_shipment(%s) failed for user %s: %s", shipment_id, current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))

    if not deleted:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    return {"message": "Shipment deleted successfully"}
