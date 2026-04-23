from fastapi import HTTPException
import asyncpg

from app.dto.category import CategoryCreate,CategoryRead,CategoryUpdate
from app.repositories import category_repo

async def create_category(
    conn: asyncpg.Connection,
    body: CategoryCreate,
    current_user: dict,
) -> CategoryRead:
    return await category_repo.create_category(
        conn, body, created_by=current_user["user_id"]
    )

async def get_category(
    conn: asyncpg.Connection, category_id: str
) -> CategoryRead:
    category = await category_repo.get_category(conn, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
 

async def list_categories(
    conn: asyncpg.Connection, offset: int, limit: int
) -> list[CategoryRead]:
    return await category_repo.list_category(conn, offset, limit)

async def update_category(
    conn: asyncpg.Connection,
    category_id: str,
    body: CategoryUpdate,
    current_user: dict,
) -> CategoryRead:
    category = await category_repo.update_category(
        conn, category_id, body, updated_by=current_user["user_id"]
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
 
async def delete_category(
    conn: asyncpg.Connection, category_id: str, current_user: dict
) -> None:
    deleted = await category_repo.delete_category(
        conn, category_id, deleted_by=current_user["user_id"]
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")