from uuid import uuid4
from typing import Optional
import asyncpg


from app.dto.category import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate
)

async def create_category(
    conn: asyncpg.Connection, data: CategoryCreate, created_by: Optional[str] = None
) -> CategoryRead:
    row = await conn.fetchrow(
        """
        INSERT INTO categories (category_id, category_name, description, parent_category_id, created_by, updated_by)
        VALUES ($1, $2, $3, $4, $5, $5)
        RETURNING category_id, category_name, description, parent_category_id,
                  created_at, updated_at, created_by, updated_by
        """,
        str(uuid4()), data.category_name, data.description, data.parent_category_id, created_by,
    )
    return CategoryRead(**dict(row))


async def get_category(conn: asyncpg.Connection, category_id: str) -> Optional[CategoryRead]:
    row = await conn.fetchrow(
        """
        SELECT category_id, category_name, description, parent_category_id,
               created_at, updated_at, created_by, updated_by
        FROM categories
        WHERE category_id = $1 AND deleted = FALSE
        """,
        category_id,
    )
    if not row:
        return None
    return CategoryRead(**dict(row))


async def list_category(
    conn: asyncpg.Connection, offset: int = 0, limit: int = 100
) -> list[CategoryRead]:
    rows = await conn.fetch(
        """
        SELECT category_id, category_name, description, parent_category_id,
               created_at, updated_at, created_by, updated_by
        FROM categories
        WHERE deleted = FALSE
        ORDER BY category_name
        LIMIT $1 OFFSET $2
        """,
        limit, offset,
    )
    return [CategoryRead(**dict(r)) for r in rows]


async def update_category(
    conn: asyncpg.Connection, category_id: str, data: CategoryUpdate, updated_by: Optional[str] = None
) -> Optional[CategoryRead]:  # Fix: was CategoryUpdate, should be CategoryRead
    row = await conn.fetchrow(
        """
        UPDATE categories
        SET
            category_name = COALESCE($1, category_name),
            description = COALESCE($2, description),
            parent_category_id = COALESCE($3, parent_category_id),
            updated_by = $4,
            updated_at = CURRENT_TIMESTAMP
        WHERE category_id = $5 AND deleted = FALSE
        RETURNING category_id, category_name, description, parent_category_id,
                  created_at, updated_at, created_by, updated_by
        """,
        data.category_name, data.description, data.parent_category_id, updated_by, category_id,
    )
    return CategoryRead(**dict(row)) if row else None


async def delete_category(
    conn: asyncpg.Connection, category_id: str, deleted_by: Optional[str] = None
) -> bool:
    result = await conn.execute(
        """
        UPDATE categories
        SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
        WHERE category_id = $1 AND deleted = FALSE
        """,
        category_id, deleted_by,
    )
    return result == "UPDATE 1"