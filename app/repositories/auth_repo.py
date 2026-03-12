"""
Database queries for users and registration requests.
"""

from typing import Optional
from uuid import uuid4

import asyncpg

from app.dto.auth import (
    RegistrationRequestCreate,
    RegistrationRequestRead,
    UserRead,
)


# ── Registration Requests ────────────────────────────────────────────

async def create_registration_request(
    conn: asyncpg.Connection, data: RegistrationRequestCreate
) -> RegistrationRequestRead:
    row = await conn.fetchrow(
        """
        INSERT INTO registration_requests
            (request_id, name, email, phone, company_name, message)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING request_id, name, email, phone, company_name,
                  message, status, created_at
        """,
        str(uuid4()),
        data.name,
        data.email,
        data.phone,
        data.company_name,
        data.message,
    )
    return RegistrationRequestRead(**dict(row))


async def list_pending_requests(
    conn: asyncpg.Connection,
) -> list[RegistrationRequestRead]:
    rows = await conn.fetch(
        """
        SELECT request_id, name, email, phone, company_name,
               message, status, created_at
        FROM   registration_requests
        WHERE  status = 'PENDING'
        ORDER  BY created_at
        """
    )
    return [RegistrationRequestRead(**dict(r)) for r in rows]


async def get_request_by_id(
    conn: asyncpg.Connection, request_id: str
) -> Optional[RegistrationRequestRead]:
    row = await conn.fetchrow(
        """
        SELECT request_id, name, email, phone, company_name,
               message, status, created_at
        FROM   registration_requests
        WHERE  request_id = $1
        """,
        request_id,
    )
    return RegistrationRequestRead(**dict(row)) if row else None


async def update_request_status(
    conn: asyncpg.Connection, request_id: str, status: str, reviewed_by: str
) -> None:
    await conn.execute(
        """
        UPDATE registration_requests
        SET    status = $1, reviewed_by = $2, updated_at = CURRENT_TIMESTAMP
        WHERE  request_id = $3
        """,
        status,
        reviewed_by,
        request_id,
    )


# ── Users ────────────────────────────────────────────────────────────

async def create_user(
    conn: asyncpg.Connection,
    *,
    name: str,
    email: str,
    password_hash: str,
    phone_number: Optional[str],
    role: str,
    supplier_id: Optional[str],
    created_by: str,
) -> UserRead:
    user_id = str(uuid4())
    row = await conn.fetchrow(
        """
        INSERT INTO users
            (user_id, name, email, password_hash, phone_number,
             role, supplier_id, is_active, created_by)
        VALUES ($1, $2, $3, $4, $5, $6, $7, TRUE, $8)
        RETURNING user_id, name, email, role, supplier_id, is_active
        """,
        user_id,
        name,
        email,
        password_hash,
        phone_number,
        role,
        supplier_id,
        created_by,
    )
    return UserRead(**dict(row))


async def get_user_by_email(
    conn: asyncpg.Connection, email: str
) -> Optional[dict]:
    """Return full user row (including password_hash) for login verification."""
    row = await conn.fetchrow(
        """
        SELECT user_id, name, email, password_hash, role,
               supplier_id, is_active
        FROM   users
        WHERE  email = $1 AND deleted = FALSE
        """,
        email,
    )
    return dict(row) if row else None


async def get_user_by_id(
    conn: asyncpg.Connection, user_id: str
) -> Optional[UserRead]:
    row = await conn.fetchrow(
        """
        SELECT user_id, name, email, role, supplier_id, is_active
        FROM   users
        WHERE  user_id = $1 AND deleted = FALSE
        """,
        user_id,
    )
    return UserRead(**dict(row)) if row else None
