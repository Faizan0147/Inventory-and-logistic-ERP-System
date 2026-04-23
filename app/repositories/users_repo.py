from uuid import uuid4
from typing import Optional
import asyncpg

from app.dto.users import (
    UserCreate,
    UserUpdate,
    UserRead,
)


async def create_user(
    conn: asyncpg.Connection, data: UserCreate, password_hash: str, created_by: Optional[str] = None
) -> UserRead:
    row = await conn.fetchrow(
        """
        INSERT INTO users (user_id, name, email, password_hash, phone_number, role, is_active, created_by, updated_by)
        VALUES ($1, $2, $3, $4, $5, $6, TRUE, $7, $7)
        RETURNING user_id, name, email, phone_number, role, is_active,
                  created_at, updated_at, created_by, updated_by
        """,
        str(uuid4()), 
        data.name, 
        data.email, 
        password_hash, 
        data.phone_number,
        data.role, 
        created_by,
    )
    return UserRead(**dict(row))


async def get_user_by_email(conn: asyncpg.Connection, email: str) -> Optional[dict]:
    row = await conn.fetchrow(
        """
        SELECT user_id, name, email, password_hash, phone_number, role, is_active
        FROM users
        WHERE email = $1 AND deleted = FALSE
        """,
        email,
    )
    return dict(row) if row else None


async def get_user(conn: asyncpg.Connection, user_id: str) -> Optional[UserRead]:
    row = await conn.fetchrow(
        """
        SELECT user_id, name, email, phone_number, role, is_active,
               created_at, updated_at, created_by, updated_by
        FROM users
        WHERE user_id = $1 AND deleted = FALSE
        """,
        user_id,
    )
    if not row:
        return None
    return UserRead(**dict(row))


async def list_users(
    conn: asyncpg.Connection, offset: int = 0, limit: int = 100
) -> list[UserRead]:
    rows = await conn.fetch(
        """
        SELECT user_id, name, email, phone_number, role, is_active,
               created_at, updated_at, created_by, updated_by
        FROM users
        WHERE deleted = FALSE
        ORDER BY name
        LIMIT $1 OFFSET $2
        """,
        limit, offset,
    )
    return [UserRead(**dict(r)) for r in rows]


async def update_user(
    conn: asyncpg.Connection, user_id: str, data: UserUpdate, password_hash: Optional[str] = None, updated_by: Optional[str] = None
) -> Optional[UserRead]:
    row = await conn.fetchrow(
        """
        UPDATE users
        SET
            name = COALESCE($1, name),
            email = COALESCE($2, email),
            password_hash = COALESCE($3, password_hash),
            phone_number = COALESCE($4, phone_number),
            role = COALESCE($5, role),
            is_active = COALESCE($6, is_active),
            updated_by = $7,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = $8 AND deleted = FALSE
        RETURNING user_id, name, email, phone_number, role, is_active,
                  created_at, updated_at, created_by, updated_by
        """,
        data.name, data.email, password_hash, data.phone_number,
        data.role, data.is_active, updated_by, user_id,
    )
    return UserRead(**dict(row)) if row else None


async def delete_user(
    conn: asyncpg.Connection, user_id: str, deleted_by: Optional[str] = None
) -> bool:
    result = await conn.execute(
        """
        UPDATE users
        SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
        WHERE user_id = $1 AND deleted = FALSE
        """,
        user_id, deleted_by,
    )
    return result == "UPDATE 1"