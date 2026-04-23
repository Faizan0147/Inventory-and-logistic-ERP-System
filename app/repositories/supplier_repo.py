from uuid import uuid4
import logging
from typing import Optional
import asyncpg

from app.dto.supplier import (
    SupplierCreate,
    SupplierUpdate,
    SupplierRead,
)


logger = logging.getLogger(__name__)


async def create_supplier(
    conn: asyncpg.Connection,
    data: SupplierCreate,
    user_id: str,
    created_by: Optional[str] = None,
    ) -> SupplierRead:
    try:
        row = await conn.fetchrow(
            """
            INSERT INTO suppliers (
                supplier_id, user_id, supplier_name, contact_email,
                contact_phone, address, status, created_by, updated_by
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING supplier_id, user_id, supplier_name, contact_email,
                      contact_phone, address, status,
                      created_at, updated_at, created_by, updated_by
            """,
            str(uuid4()),
            user_id,
            data.supplier_name,
            data.contact_email,
            data.contact_phone,
            data.address,
            data.status,
            created_by,
            created_by,
        )
        return SupplierRead(**dict(row))

    except asyncpg.UniqueViolationError:
        logger.warning("create_supplier: duplicate email '%s'", data.contact_email)
        raise ValueError("A supplier with this email already exists.")
        
    except asyncpg.ForeignKeyViolationError as e:
        logger.warning("create_supplier: foreign key violation — %s", e)
        raise ValueError("Invalid user_id.")

    except asyncpg.PostgresError as e:
        logger.error("create_supplier: database error — %s", e)
        raise RuntimeError(f"Database error while creating supplier: {e}")

async def get_supplier(
    conn: asyncpg.Connection,
    supplier_id: str,
    user_id: Optional[str] = None,
    ) -> Optional[SupplierRead]:

    try:
        query = """
            SELECT supplier_id, user_id, supplier_name, contact_email,
                   contact_phone, address, status,
                   created_at, updated_at, created_by, updated_by
            FROM suppliers
            WHERE supplier_id = $1
            AND deleted = FALSE
        """

        params = [supplier_id]
        if user_id:
            query += " AND user_id = $2"
            params.append(user_id)

        row = await conn.fetchrow(query, *params)
        if not row:
            return None

        return SupplierRead(**dict(row))
        
    except asyncpg.PostgresError as e:
        logger.error("get_supplier(%s): database error — %s", supplier_id, e)
        raise RuntimeError(f"Database error while fetching supplier: {e}")

async def list_suppliers(
    conn: asyncpg.Connection,
    offset: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    ) -> list[SupplierRead]:

    try:
        query = """
            SELECT supplier_id, user_id, supplier_name, contact_email,
                   contact_phone, address, status,
                   created_at, updated_at, created_by, updated_by
            FROM suppliers
            WHERE deleted = FALSE
        """

        params = [limit, offset]
        if user_id:
            query += " AND user_id = $3"
            params.append(user_id)

        query += " ORDER BY supplier_name LIMIT $1 OFFSET $2"
        rows = await conn.fetch(query, *params)
        return [SupplierRead(**dict(r)) for r in rows]
        
    except asyncpg.PostgresError as e:
        logger.error("list_suppliers: database error — %s", e)
        raise RuntimeError(f"Database error while listing suppliers: {e}")

async def update_supplier(
    conn: asyncpg.Connection,
    supplier_id: str,
    data: SupplierUpdate,
    updated_by: Optional[str] = None,
    user_id: Optional[str] = None,
    ) -> Optional[SupplierRead]:
    
    try:
        row = await conn.fetchrow(
            """
            UPDATE suppliers
            SET
                supplier_name = COALESCE($1, supplier_name),
                contact_email = COALESCE($2, contact_email),
                contact_phone = COALESCE($3, contact_phone),
                address       = COALESCE($4, address),
                status        = COALESCE($5, status),
                updated_by    = $6,
                updated_at    = CURRENT_TIMESTAMP
            WHERE supplier_id = $7
              AND deleted = FALSE
              AND user_id = $8
            RETURNING supplier_id, user_id, supplier_name, contact_email,
                      contact_phone, address, status,
                      created_at, updated_at, created_by, updated_by
            """,
            data.supplier_name,
            data.contact_email,
            data.contact_phone,
            data.address,
            data.status,
            updated_by,
            supplier_id,
            user_id,
        )
        return SupplierRead(**dict(row)) if row else None
        
    except asyncpg.UniqueViolationError:
        logger.warning("update_supplier(%s): duplicate email '%s'", supplier_id, data.contact_email)
        raise ValueError("A supplier with this email already exists.")

    except asyncpg.PostgresError as e:
        logger.error("update_supplier(%s): database error — %s", supplier_id, e)
        raise RuntimeError(f"Database error while updating supplier: {e}")

async def delete_supplier(
    conn: asyncpg.Connection,
    supplier_id: str,
    deleted_by: Optional[str] = None,
    user_id: Optional[str] = None,
    ) -> bool:

    try:
        result = await conn.execute(
            """
            UPDATE suppliers
            SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
            WHERE supplier_id = $1
              AND deleted = FALSE
              AND user_id = $3
            """,
            supplier_id,
            deleted_by,
            user_id,
        )
        return result == "UPDATE 1"
    
    except asyncpg.PostgresError as e:
        logger.error("delete_supplier(%s): database error — %s", supplier_id, e)
        raise RuntimeError(f"Database error while deleting supplier: {e}")
