import logging
from uuid import uuid4
from typing import Optional

import asyncpg

from app.dto.users import UserCreate, UserUpdate, UserRead

logger = logging.getLogger(__name__)


async def create_user(
    conn: asyncpg.Connection,
    data: UserCreate,
    password_hash: str,
    created_by: Optional[str] = None,
) -> UserRead:
    logger.debug("Creating user email=%s role=%s", data.email, data.role)
    row = await conn.fetchrow(
        """
        INSERT INTO users
            (user_id, name, email, password_hash, phone_number, role, is_active, created_by, updated_by)
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
    logger.debug("Fetching user by email=%s", email)
    row = await conn.fetchrow(
        """
        SELECT user_id, name, email, password_hash, phone_number, role, is_active
        FROM   users
        WHERE  email = $1 AND deleted = FALSE
        """,
        email,
    )
    return dict(row) if row else None


async def get_user(
    conn: asyncpg.Connection,
    user_id: str,
    current_user_id: Optional[str] = None,
) -> Optional[UserRead]:
    logger.debug("Fetching user by user_id=%s", user_id)
    query = """
        SELECT user_id, name, email, phone_number, role, is_active,
               created_at, updated_at, created_by, updated_by
        FROM   users
        WHERE  user_id = $1 AND deleted = FALSE
    """
    params = [user_id]
    if current_user_id:
        query += " AND user_id = $2"
        params.append(current_user_id)

    row = await conn.fetchrow(query, *params)
    return UserRead(**dict(row)) if row else None


async def list_users(
    conn: asyncpg.Connection, 
    offset: int = 0, 
    limit: int = 100,
    
) -> list[UserRead]:
    logger.debug("Listing users offset=%d limit=%d", offset, limit)
    rows = await conn.fetch(
        """
        SELECT user_id, name, email, phone_number, role, is_active,
               created_at, updated_at, created_by, updated_by
        FROM   users
        WHERE  deleted = FALSE
        ORDER  BY name
        LIMIT  $1 OFFSET $2
        """,
        limit,
        offset,
    )
    return [UserRead(**dict(r)) for r in rows]


async def update_user(
    conn: asyncpg.Connection,
    user_id: str,
    data: UserUpdate,
    password_hash: Optional[str] = None,
    updated_by: Optional[str] = None,
    current_user_id: Optional[str] = None,
) -> Optional[UserRead]:
    logger.debug("Updating user user_id=%s", user_id)
    query = """
        UPDATE users
        SET
            name          = COALESCE($1, name),
            email         = COALESCE($2, email),
            password_hash = COALESCE($3, password_hash),
            phone_number  = COALESCE($4, phone_number),
            role          = COALESCE($5, role),
            is_active     = COALESCE($6, is_active),
            updated_by    = $7,
            updated_at    = CURRENT_TIMESTAMP
        WHERE user_id = $8 AND deleted = FALSE
    """
    params = [
        data.name, data.email, password_hash, data.phone_number,
        data.role, data.is_active, updated_by, user_id,
    ]
    if current_user_id:
        query += " AND user_id = $9"
        params.append(current_user_id)

    query += """
        RETURNING user_id, name, email, phone_number, role, is_active,
                  created_at, updated_at, created_by, updated_by
    """
    row = await conn.fetchrow(query, *params)
    return UserRead(**dict(row)) if row else None


async def delete_user(
    conn: asyncpg.Connection,
    user_id: str,
    deleted_by: Optional[str] = None,
    current_user_id: Optional[str] = None,
) -> bool:
    logger.debug("Soft-deleting user user_id=%s", user_id)
    query = """
        UPDATE users
        SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
        WHERE user_id = $1 AND deleted = FALSE
    """
    params = [user_id, deleted_by]
    if current_user_id:
        query += " AND user_id = $3"
        params.append(current_user_id)

    result = await conn.execute(query, *params)
    return result == "UPDATE 1"
