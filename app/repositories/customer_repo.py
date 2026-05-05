import logging
from uuid import uuid4
from typing import Optional
import asyncpg

from app.dto.customers import CustomerCreate, CustomerUpdate, CustomerRead

logger = logging.getLogger(__name__)

_RETURNING = """
    RETURNING customer_id, user_id, customer_name, contact_person, phone, email,
              address, customer_type, created_at, updated_at, created_by, updated_by
"""


async def create_customer(
    conn: asyncpg.Connection,
    data: CustomerCreate,
    user_id: str,
    created_by: Optional[str] = None,
) -> CustomerRead:
    try:
        row = await conn.fetchrow(
            f"""
            INSERT INTO customers (
                customer_id, user_id, customer_name, contact_person,
                phone, email, address, customer_type, created_by, updated_by
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $9)
            {_RETURNING}
            """,
            str(uuid4()),
            user_id,
            data.customer_name,
            data.contact_person,
            data.phone,
            data.email,
            data.address,
            data.customer_type,
            created_by,
        )
        return CustomerRead(**dict(row))

    except asyncpg.UniqueViolationError:
        logger.warning("create_customer: duplicate email '%s'", data.email)
        raise ValueError(f"A customer with email '{data.email}' already exists.")

    except asyncpg.PostgresError as e:
        logger.error("create_customer: database error — %s", e)
        raise RuntimeError(f"Database error while creating customer: {e}")


async def get_customer(
    conn: asyncpg.Connection,
    customer_id: str,
    user_id: Optional[str] = None,
) -> Optional[CustomerRead]:
    try:
        query = """
            SELECT customer_id, user_id, customer_name, contact_person, phone, email,
                   address, customer_type, created_at, updated_at, created_by, updated_by
            FROM customers
            WHERE customer_id = $1 AND deleted = FALSE
        """
        params = [customer_id]
        if user_id:
            query += " AND user_id = $2"
            params.append(user_id)

        row = await conn.fetchrow(query, *params)
        return CustomerRead(**dict(row)) if row else None

    except asyncpg.PostgresError as e:
        logger.error("get_customer(%s): database error — %s", customer_id, e)
        raise RuntimeError(f"Database error while fetching customer: {e}")


async def list_customers(
    conn: asyncpg.Connection,
    offset: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
) -> list[CustomerRead]:
    try:
        query = """
            SELECT customer_id, user_id, customer_name, contact_person, phone, email,
                   address, customer_type, created_at, updated_at, created_by, updated_by
            FROM customers
            WHERE deleted = FALSE
        """
        params = [limit, offset]
        if user_id:
            query += " AND user_id = $3"
            params.append(user_id)

        query += " ORDER BY customer_name LIMIT $1 OFFSET $2"
        rows = await conn.fetch(query, *params)
        return [CustomerRead(**dict(r)) for r in rows]

    except asyncpg.PostgresError as e:
        logger.error("list_customers: database error — %s", e)
        raise RuntimeError(f"Database error while listing customers: {e}")


async def update_customer(
    conn: asyncpg.Connection,
    customer_id: str,
    data: CustomerUpdate,
    updated_by: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Optional[CustomerRead]:
    try:
        query = f"""
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
        """
        params = [
            data.customer_name,
            data.contact_person,
            data.phone,
            data.email,
            data.address,
            data.customer_type,
            updated_by,
            customer_id,
        ]
        if user_id:
            query += " AND user_id = $9"
            params.append(user_id)

        query += _RETURNING
        row = await conn.fetchrow(query, *params)
        return CustomerRead(**dict(row)) if row else None

    except asyncpg.UniqueViolationError:
        logger.warning(
            "update_customer(%s): duplicate email '%s'", customer_id, data.email
        )
        raise ValueError(f"A customer with email '{data.email}' already exists.")

    except asyncpg.PostgresError as e:
        logger.error("update_customer(%s): database error — %s", customer_id, e)
        raise RuntimeError(f"Database error while updating customer: {e}")


async def delete_customer(
    conn: asyncpg.Connection,
    customer_id: str,
    deleted_by: Optional[str] = None,
    user_id: Optional[str] = None,
) -> bool:
    try:
        query = """
            UPDATE customers
            SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
            WHERE customer_id = $1 AND deleted = FALSE
        """
        params = [customer_id, deleted_by]
        if user_id:
            query += " AND user_id = $3"
            params.append(user_id)

        result = await conn.execute(query, *params)
        return result == "UPDATE 1"

    except asyncpg.PostgresError as e:
        logger.error("delete_customer(%s): database error — %s", customer_id, e)
        raise RuntimeError(f"Database error while deleting customer: {e}")
