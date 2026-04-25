import logging
from fastapi import HTTPException
import asyncpg

from app.dto.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.repositories import category_repo

logger = logging.getLogger(__name__)


def _get_current_user(current_user: dict) -> str | None:
    """Return user_id for SUPPLIER (scoped access), None for ADMIN (full access)."""
    return current_user["user_id"] if current_user["role"] == "SUPPLIER" else None


async def create_category(
    conn: asyncpg.Connection,
    body: CategoryCreate,
    current_user: dict,
) -> CategoryRead:
    try:
        return await category_repo.create_category(
            conn, body, user_id=current_user["user_id"], created_by=current_user["user_id"]
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except RuntimeError as e:
        logger.error("create_category failed for user %s: %s", current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))


async def get_category(
    conn: asyncpg.Connection, 
    category_id: str,
    current_user: dict
) -> CategoryRead:
    try:
        category = await category_repo.get_category(
            conn, category_id, user_id=_get_current_user(current_user)
        )
    except RuntimeError as e:
        logger.error("get_category(%s) failed for user %s: %s", category_id, current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


async def list_categories(
    conn: asyncpg.Connection, 
    offset: int, 
    limit: int,
    current_user: dict
) -> list[CategoryRead]:
    try:
        return await category_repo.list_categories(
            conn, offset, limit, user_id=_get_current_user(current_user)
        )
    except RuntimeError as e:
        logger.error("list_categories failed for user %s: %s", current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))


async def update_category(
    conn: asyncpg.Connection,
    category_id: str,
    body: CategoryUpdate,
    current_user: dict,
) -> CategoryRead:
    try:
        category = await category_repo.update_category(
            conn, category_id, body, 
            updated_by=current_user["user_id"],
            user_id=_get_current_user(current_user)
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except RuntimeError as e:
        logger.error("update_category(%s) failed for user %s: %s", category_id, current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))

    if not category:
        raise HTTPException(status_code=404, detail="Category not found or access denied")
    return category


async def delete_category(
    conn: asyncpg.Connection, 
    category_id: str, 
    current_user: dict
) -> None:
    try:
        deleted = await category_repo.delete_category(
            conn, category_id, 
            deleted_by=current_user["user_id"],
            user_id=_get_current_user(current_user)
        )
    except RuntimeError as e:
        logger.error("delete_category(%s) failed for user %s: %s", category_id, current_user["user_id"], e)
        raise HTTPException(status_code=500, detail=str(e))

    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found or access denied")