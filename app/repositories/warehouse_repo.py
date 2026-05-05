import logging
from uuid import uuid4
from typing import Optional
import asyncpg
from fastapi import HTTPException
from app.dto.warehouse import WarehouseCreate, WarehouseRead, WarehouseUpdate

logger = logging.getLogger(__name__)


async def create_warehouse(
    conn: asyncpg.Connection,
    data: WarehouseCreate,
    user_id: str,
    created_by: Optional[str] = None,
) -> WarehouseRead:
    try:
        row = await conn.fetchrow(
            """
            INSERT INTO warehouses (
                warehouse_id, user_id, warehouse_name, location, city, capacity, 
                phone, is_active, created_by, updated_by
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $9)
            RETURNING warehouse_id, user_id, warehouse_name, location, city, capacity, phone, is_active,
                    created_by, updated_by
            """,
            str(uuid4()),
            user_id,
            data.warehouse_name,
            data.location,
            data.city,
            data.capacity,
            data.phone,
            data.is_active,
            created_by,
        )
        return WarehouseRead(**dict(row))

    except asyncpg.UniqueViolationError:
        logger.warning(
            "create_warehouse: duplicate warehouse_name '%s'", data.warehouse_name
        )
        raise ValueError(
            f"A warehouse with name '{data.warehouse_name}' already exists."
        )

    except asyncpg.ForeignKeyViolationError as e:
        logger.warning("create_warehouse: foreign key violation — %s", e)
        raise ValueError("Invalid manager_id.")

    except asyncpg.PostgresError as e:
        logger.error("create_warehouse: database error — %s", e)
        raise RuntimeError(f"Database error while creating warehouse: {e}")


async def get_warehouse(
    conn: asyncpg.Connection, warehouse_id: str, user_id: Optional[str] = None
) -> Optional[WarehouseRead]:
    try:
        query = """
            SELECT warehouse_id, user_id, warehouse_name, location, city, capacity, phone, is_active,
                   created_at, updated_at, created_by, updated_by
            FROM warehouses
            WHERE warehouse_id = $1 AND deleted = FALSE
        """
        params = [warehouse_id]
        if user_id:
            query += " AND user_id = $2"
            params.append(user_id)

        row = await conn.fetchrow(query, *params)
        return WarehouseRead(**dict(row)) if row else None

    except asyncpg.PostgresError as e:
        logger.error("get_warehouse(%s): database error — %s", warehouse_id, e)
        raise RuntimeError(f"Database error while fetching warehouse: {e}")


async def list_warehouses(
    conn: asyncpg.Connection,
    offset: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
) -> list[WarehouseRead]:
    try:
        query = """
            SELECT warehouse_id, user_id, warehouse_name, location, city, capacity, phone, is_active,
                   created_at, updated_at, created_by, updated_by
            FROM warehouses
            WHERE deleted = FALSE
        """
        params = [limit, offset]
        if user_id:
            query += " AND user_id = $3"
            params.append(user_id)

        query += " ORDER BY warehouse_name LIMIT $1 OFFSET $2"

        rows = await conn.fetch(query, *params)
        return [WarehouseRead(**dict(r)) for r in rows]

    except asyncpg.PostgresError as e:
        logger.error("list_warehouses: database error — %s", e)
        raise RuntimeError(f"Database error while listing warehouses: {e}")


async def update_warehouse(
    conn: asyncpg.Connection,
    warehouse_id: str,
    data: WarehouseUpdate,
    updated_by: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Optional[WarehouseRead]:
    try:
        query = """
            UPDATE warehouses
            SET
                warehouse_name = COALESCE($1, warehouse_name),
                location = COALESCE($2, location),
                city = COALESCE($3, city),
                capacity = COALESCE($4, capacity),
                phone = COALESCE($5, phone),
                is_active = COALESCE($6, is_active),
                updated_by = $7,
                updated_at = CURRENT_TIMESTAMP
            WHERE warehouse_id = $8 AND deleted = FALSE
        """
        params = [
            data.warehouse_name,
            data.location,
            data.city,
            data.capacity,
            data.phone,
            data.is_active,
            updated_by,
            warehouse_id,
        ]
        if user_id:
            query += " AND user_id = $9"
            params.append(user_id)

        query += """
            RETURNING warehouse_id, user_id, warehouse_name, location, city, capacity, phone, is_active,
                      created_at, updated_at, created_by, updated_by
        """
        row = await conn.fetchrow(query, *params)
        return WarehouseRead(**dict(row)) if row else None

    except asyncpg.UniqueViolationError:
        logger.warning(
            "update_warehouse(%s): duplicate warehouse_name '%s'",
            warehouse_id,
            data.warehouse_name,
        )
        raise ValueError(
            f"A warehouse with name '{data.warehouse_name}' already exists."
        )

    except asyncpg.ForeignKeyViolationError as e:
        logger.warning(
            "update_warehouse(%s): foreign key violation — %s", warehouse_id, e
        )
        raise ValueError("Invalid manager_id.")

    except asyncpg.PostgresError as e:
        logger.error("update_warehouse(%s): database error — %s", warehouse_id, e)
        raise RuntimeError(f"Database error while updating warehouse: {e}")


async def delete_warehouse(
    conn: asyncpg.Connection,
    warehouse_id: str,
    deleted_by: Optional[str] = None,
    user_id: Optional[str] = None,
) -> bool:
    try:
        query = """
            UPDATE warehouses
            SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
            WHERE warehouse_id = $1 AND deleted = FALSE
        """
        params = [warehouse_id, deleted_by]
        if user_id:
            query += " AND user_id = $3"
            params.append(user_id)

        result = await conn.execute(query, *params)
        return result == "UPDATE 1"

    except asyncpg.PostgresError as e:
        logger.error("delete_warehouse(%s): database error — %s", warehouse_id, e)
        raise RuntimeError(f"Database error while deleting warehouse: {e}")
