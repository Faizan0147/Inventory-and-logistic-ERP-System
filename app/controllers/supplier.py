import logging
from fastapi import HTTPException
import asyncpg

from app.dto.supplier import SupplierCreate, SupplierUpdate, SupplierRead
from app.repositories import supplier_repo

logger = logging.getLogger(__name__)


def _resolve_user_id(current_user: dict) -> str | None:
    return current_user["user_id"] if current_user["role"] == "SUPPLIER" else None


async def create_supplier(
    conn: asyncpg.Connection,
    body: SupplierCreate,
    current_user: dict,
) -> SupplierRead:

    try:
        return await supplier_repo.create_supplier(
            conn,
            body,
            user_id=current_user["user_id"],
            created_by=current_user["user_id"],
        )

    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    except RuntimeError as e:
        logger.error(
            "create_supplier failed for user %s: %s", current_user["user_id"], e
        )
        raise HTTPException(status_code=500, detail=str(e))


async def list_suppliers(
    conn: asyncpg.Connection,
    offset: int,
    limit: int,
    current_user: dict,
) -> list[SupplierRead]:

    try:
        return await supplier_repo.list_suppliers(
            conn,
            offset,
            limit,
            user_id=_resolve_user_id(current_user),
        )

    except RuntimeError as e:
        logger.error(
            "list_suppliers failed for user %s: %s", current_user["user_id"], e
        )
        raise HTTPException(status_code=500, detail=str(e))


async def get_supplier(
    conn: asyncpg.Connection,
    supplier_id: str,
    current_user: dict,
) -> SupplierRead:

    try:
        supplier = await supplier_repo.get_supplier(
            conn,
            supplier_id,
            user_id=_resolve_user_id(current_user),
        )

    except RuntimeError as e:
        logger.error(
            "get_supplier(%s) failed for user %s: %s",
            supplier_id,
            current_user["user_id"],
            e,
        )
        raise HTTPException(status_code=500, detail=str(e))

    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


async def update_supplier(
    conn: asyncpg.Connection,
    supplier_id: str,
    body: SupplierUpdate,
    current_user: dict,
) -> SupplierRead:

    try:
        supplier = await supplier_repo.update_supplier(
            conn,
            supplier_id,
            body,
            updated_by=current_user["user_id"],
            user_id=_resolve_user_id(current_user),
        )

    except RuntimeError as e:
        logger.error(
            "update_supplier(%s) failed for user %s: %s",
            supplier_id,
            current_user["user_id"],
            e,
        )
        raise HTTPException(status_code=500, detail=str(e))

    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


async def delete_supplier(
    conn: asyncpg.Connection,
    supplier_id: str,
    current_user: dict,
) -> dict:

    try:
        deleted = await supplier_repo.delete_supplier(
            conn,
            supplier_id,
            deleted_by=current_user["user_id"],
            user_id=_resolve_user_id(current_user),
        )

    except RuntimeError as e:
        logger.error(
            "delete_supplier(%s) failed for user %s: %s",
            supplier_id,
            current_user["user_id"],
            e,
        )
        raise HTTPException(status_code=500, detail=str(e))

    if not deleted:
        raise HTTPException(status_code=404, detail="Supplier not found")

    return {"message": "Supplier deleted successfully"}
