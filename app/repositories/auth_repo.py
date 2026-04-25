"""
Database queries for registration requests.
"""
import logging
from typing import Optional
from uuid import uuid4

import asyncpg

from app.dto.auth import (
    RegistrationRequestCreate,
    RegistrationRequestRead,
)

logger = logging.getLogger(__name__)


async def create_registration_request(
    conn: asyncpg.Connection, 
    data: RegistrationRequestCreate
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
