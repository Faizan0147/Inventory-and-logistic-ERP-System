import logging
from fastapi import HTTPException
import asyncpg

from app.dto.product import ProductRead, ProductCreate, ProductUpdate
from app.repositories import product_repo

logger = logging.getLogger(__name__)


def _get_current_user(current_user: dict) -> str | None:
    """Return user_id for SUPPLIER (scoped access), None for ADMIN (full access)."""
    return current_user["user_id"] if current_user["role"] == "SUPPLIER" else None


async def create_product(
    conn: asyncpg.Connection,
    body: ProductCreate,
    current_user: dict,
) -> ProductRead:

    try:
        return await product_repo.create_product(
            conn,
            body,
            user_id=current_user["user_id"],
            created_by=current_user["user_id"],
        )

    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    except RuntimeError as e:
        logger.error(
            "create_product failed for user %s: %s", current_user["user_id"], e
        )
        raise HTTPException(status_code=500, detail=str(e))


async def get_product(
    conn: asyncpg.Connection, product_id: str, current_user: dict
) -> ProductRead:

    try:
        product = await product_repo.get_product(
            conn, product_id, user_id=_get_current_user(current_user)
        )

    except RuntimeError as e:
        logger.error(
            "get_product(%s) failed for user %s: %s",
            product_id,
            current_user["user_id"],
            e,
        )
        raise HTTPException(status_code=500, detail=str(e))

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


async def list_products(
    conn: asyncpg.Connection, offset: int, limit: int, current_user: dict
) -> list[ProductRead]:

    try:
        return await product_repo.list_products(
            conn, offset, limit, user_id=_get_current_user(current_user)
        )

    except RuntimeError as e:
        logger.error("list_products failed for user %s: %s", current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))


async def update_product(
    conn: asyncpg.Connection,
    product_id: str,
    body: ProductUpdate,
    current_user: dict,
) -> ProductRead:

    try:
        product = await product_repo.update_product(
            conn,
            product_id,
            body,
            updated_by=current_user["user_id"],
            user_id=_get_current_user(current_user),
        )

    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    except RuntimeError as e:
        logger.error(
            "update_product(%s) failed for user %s: %s",
            product_id,
            current_user["user_id"],
            e,
        )
        raise HTTPException(status_code=500, detail=str(e))

    if not product:
        raise HTTPException(
            status_code=404, detail="Product not found or access denied"
        )
    return product


async def delete_product(
    conn: asyncpg.Connection, product_id: str, current_user: dict
) -> dict:

    try:
        deleted = await product_repo.delete_product(
            conn,
            product_id,
            deleted_by=current_user["user_id"],
            user_id=_get_current_user(current_user),
        )

    except RuntimeError as e:
        logger.error(
            "delete_product(%s) failed for user %s: %s",
            product_id,
            current_user["user_id"],
            e,
        )
        raise HTTPException(status_code=500, detail=str(e))

    if not deleted:
        raise HTTPException(
            status_code=404, detail="Product not found or access denied"
        )

    return {"message": "Product deleted successfully"}
