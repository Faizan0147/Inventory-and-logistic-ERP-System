from uuid import uuid4
from typing import Optional
import asyncpg

from app.dto.customers import CustomerCreate, CustomerUpdate, CustomerRead


async def create_customer(
    conn: asyncpg.Connection,
    data: CustomerCreate,
    created_by: Optional[str] = None,
) -> CustomerRead:
    row = await conn.fetchrow(
        """
        INSERT INTO customers
            (customer_id, customer_name, contact_person, phone, email,
             address, customer_type, created_by, updated_by)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $8)
        RETURNING customer_id, customer_name, contact_person, phone, email,
                  address, customer_type, created_at, updated_at, created_by, updated_by
        """,
        str(uuid4()), data.customer_name, data.contact_person, data.phone,
        data.email, data.address, data.customer_type, created_by,
    )
    return CustomerRead(**dict(row))


async def get_customer(
    conn: asyncpg.Connection, customer_id: str
) -> Optional[CustomerRead]:
    row = await conn.fetchrow(
        """
        SELECT customer_id, customer_name, contact_person, phone, email,
               address, customer_type, created_at, updated_at, created_by, updated_by
        FROM customers
        WHERE customer_id = $1 AND deleted = FALSE
        """,
        customer_id,
    )
    return CustomerRead(**dict(row)) if row else None


async def list_customers(
    conn: asyncpg.Connection,
    offset: int = 0,
    limit: int = 100,
) -> list[CustomerRead]:
    rows = await conn.fetch(
        """
        SELECT customer_id, customer_name, contact_person, phone, email,
               address, customer_type, created_at, updated_at, created_by, updated_by
        FROM customers
        WHERE deleted = FALSE
        ORDER BY customer_name
        LIMIT $1 OFFSET $2
        """,
        limit, offset,
    )
    return [CustomerRead(**dict(r)) for r in rows]


async def update_customer(
    conn: asyncpg.Connection,
    customer_id: str,
    data: CustomerUpdate,
    updated_by: Optional[str] = None,
) -> Optional[CustomerRead]:
    row = await conn.fetchrow(
        """
        UPDATE customers
        SET
            customer_name  = COALESCE($1, customer_name),
            contact_person = COALESCE($2, contact_person),
            phone          = COALESCE($3, phone),
            email          = COALESCE($4, email),
            address        = COALESCE($5, address),
            customer_type  = COALESCE($6, customer_type),
            updated_by     = $7,
            updated_at     = CURRENT_TIMESTAMP
        WHERE customer_id = $8 AND deleted = FALSE
        RETURNING customer_id, customer_name, contact_person, phone, email,
                  address, customer_type, created_at, updated_at, created_by, updated_by
        """,
        data.customer_name, data.contact_person, data.phone, data.email,
        data.address, data.customer_type, updated_by, customer_id,
    )
    return CustomerRead(**dict(row)) if row else None


async def delete_customer(
    conn: asyncpg.Connection,
    customer_id: str,
    deleted_by: Optional[str] = None,
) -> bool:
    result = await conn.execute(
        """
        UPDATE customers
        SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
        WHERE customer_id = $1 AND deleted = FALSE
        """,
        customer_id, deleted_by,
    )
    return result == "UPDATE 1"