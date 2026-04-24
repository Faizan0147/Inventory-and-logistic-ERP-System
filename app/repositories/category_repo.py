import logging
from uuid import uuid4
from typing import Optional
import asyncpg

from app.dto.category import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate
)

logger = logging.getLogger(__name__)


async def create_category(
    conn: asyncpg.Connection, 
    data: CategoryCreate, 
    user_id: str,
    created_by: Optional[str] = None
) -> CategoryRead:
    try:
        row = await conn.fetchrow(
            """
            INSERT INTO categories (
                category_id, user_id, category_name, description, 
                parent_category_id, created_by, updated_by
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING category_id, user_id, category_name, description, parent_category_id,
                      created_at, updated_at, created_by, updated_by
            """,
            str(uuid4()), 
            user_id,
            data.category_name, 
            data.description, 
            data.parent_category_id, 
            created_by,
            created_by,
        )
        return CategoryRead(**dict(row))

    except asyncpg.UniqueViolationError:
        logger.warning("create_category: duplicate category_name '%s'", data.category_name)
        raise ValueError(f"A category with name '{data.category_name}' already exists.")

    except asyncpg.ForeignKeyViolationError as e:
        logger.warning("create_category: foreign key violation — %s", e)
        raise ValueError("Invalid parent_category_id.")

    except asyncpg.PostgresError as e:
        logger.error("create_category: database error — %s", e)
        raise RuntimeError(f"Database error while creating category: {e}")


async def get_category(
    conn: asyncpg.Connection, 
    category_id: str,
    user_id: Optional[str] = None
) -> Optional[CategoryRead]:
    try:
        query = """
            SELECT category_id, user_id, category_name, description, parent_category_id,
                   created_at, updated_at, created_by, updated_by
            FROM categories
            WHERE category_id = $1 AND deleted = FALSE
        """
        params = [category_id]
        if user_id:
            query += " AND user_id = $2"
            params.append(user_id)

        row = await conn.fetchrow(query, *params)
        return CategoryRead(**dict(row)) if row else None

    except asyncpg.PostgresError as e:
        logger.error("get_category(%s): database error — %s", category_id, e)
        raise RuntimeError(f"Database error while fetching category: {e}")


async def list_categories(
    conn: asyncpg.Connection, 
    offset: int = 0, 
    limit: int = 100,
    user_id: Optional[str] = None
) -> list[CategoryRead]:
    try:
        query = """
            SELECT category_id, user_id, category_name, description, parent_category_id,
                   created_at, updated_at, created_by, updated_by
            FROM categories
            WHERE deleted = FALSE
        """
        params = [limit, offset]
        if user_id:
            query += " AND user_id = $3"
            params.append(user_id)

        query += " ORDER BY category_name LIMIT $1 OFFSET $2"

        rows = await conn.fetch(query, *params)
        return [CategoryRead(**dict(r)) for r in rows]

    except asyncpg.PostgresError as e:
        logger.error("list_categories: database error — %s", e)
        raise RuntimeError(f"Database error while listing categories: {e}")


async def update_category(
    conn: asyncpg.Connection, 
    category_id: str, 
    data: CategoryUpdate, 
    updated_by: Optional[str] = None,
    user_id: Optional[str] = None
) -> Optional[CategoryRead]:
    try:
        query = """
            UPDATE categories
            SET
                category_name = COALESCE($1, category_name),
                description = COALESCE($2, description),
                parent_category_id = COALESCE($3, parent_category_id),
                updated_by = $4,
                updated_at = CURRENT_TIMESTAMP
            WHERE category_id = $5 AND deleted = FALSE
        """
        params = [data.category_name, data.description, data.parent_category_id, updated_by, category_id]
        if user_id:
            query += " AND user_id = $6"
            params.append(user_id)

        query += """
            RETURNING category_id, user_id, category_name, description, parent_category_id,
                      created_at, updated_at, created_by, updated_by
        """
        row = await conn.fetchrow(query, *params)
        return CategoryRead(**dict(row)) if row else None

    except asyncpg.UniqueViolationError:
        logger.warning("update_category(%s): duplicate category_name '%s'", category_id, data.category_name)
        raise ValueError(f"A category with name '{data.category_name}' already exists.")

    except asyncpg.ForeignKeyViolationError as e:
        logger.warning("update_category(%s): foreign key violation — %s", category_id, e)
        raise ValueError("Invalid parent_category_id.")

    except asyncpg.PostgresError as e:
        logger.error("update_category(%s): database error — %s", category_id, e)
        raise RuntimeError(f"Database error while updating category: {e}")


async def delete_category(
    conn: asyncpg.Connection, 
    category_id: str, 
    deleted_by: Optional[str] = None,
    user_id: Optional[str] = None
) -> bool:
    try:
        query = """
            UPDATE categories
            SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
            WHERE category_id = $1 AND deleted = FALSE
        """
        params = [category_id, deleted_by]
        if user_id:
            query += " AND user_id = $3"
            params.append(user_id)

        result = await conn.execute(query, *params)
        return result == "UPDATE 1"

    except asyncpg.PostgresError as e:
        logger.error("delete_category(%s): database error — %s", category_id, e)
        raise RuntimeError(f"Database error while deleting category: {e}")