import logging
from uuid import uuid4
from typing import Optional
import asyncpg

from app.dto.product import (
    ProductCreate,
    ProductRead,
    ProductUpdate,
)

logger = logging.getLogger(__name__)


async def create_product(
    conn: asyncpg.Connection,
    data: ProductCreate, 
    user_id: str,
    created_by: Optional[str] = None
) -> ProductRead:
    try:
        row = await conn.fetchrow(
            """
            INSERT INTO products (
                product_id, supplier_id, user_id, category_id, product_name, description,
                sku, price, cost_price, weight, status,created_by, updated_by
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            RETURNING product_id, supplier_id, user_id, category_id, product_name, description,
                      sku, price, cost_price, weight, status,
                      created_at, updated_at, created_by, updated_by
            """,
            str(uuid4()), 
            data.supplier_id, 
            user_id,
            data.category_id, 
            data.product_name,
            data.description,
            data.sku, 
            data.price, 
            data.cost_price, 
            data.weight,
            data.status, 
            created_by,
        )
        return ProductRead(**dict(row))

    except asyncpg.UniqueViolationError:
        logger.warning("create_product: duplicate SKU '%s'", data.sku)
        raise ValueError(f"A product with SKU '{data.sku}' already exists.")

    except asyncpg.ForeignKeyViolationError as e:
        logger.warning("create_product: foreign key violation — %s", e)
        raise ValueError("Invalid supplier_id or category_id.")

    except asyncpg.PostgresError as e:
        logger.error("create_product: database error — %s", e)
        raise RuntimeError(f"Database error while creating product: {e}")


async def get_product(
    conn: asyncpg.Connection, 
    product_id: str, 
    user_id: Optional[str] = None
) -> Optional[ProductRead]:
    try:
        query = """
            SELECT product_id, supplier_id, category_id, product_name, description,
                   sku, price, cost_price, weight, status,
                   user_id, created_at, updated_at, created_by, updated_by
            FROM products
            WHERE product_id = $1 AND deleted = FALSE
        """
        params = [product_id]
        if user_id:
            query += " AND user_id = $2"
            params.append(user_id)

        row = await conn.fetchrow(query, *params)
        return ProductRead(**dict(row)) if row else None

    except asyncpg.PostgresError as e:
        logger.error("get_product(%s): database error — %s", product_id, e)
        raise RuntimeError(f"Database error while fetching product: {e}")


async def list_products(
    conn: asyncpg.Connection, 
    offset: int = 0, 
    limit: int = 100, 
    user_id: Optional[str] = None
) -> list[ProductRead]:
    try:
        query = """
            SELECT product_id, supplier_id, category_id, product_name, description,
                   sku, price, cost_price, weight, status,
                   user_id, created_at, updated_at, created_by, updated_by
            FROM products
            WHERE deleted = FALSE
        """
        params = [limit, offset]
        if user_id:
            query += " AND user_id = $3"
            params.append(user_id)

        query += " ORDER BY product_name LIMIT $1 OFFSET $2"

        rows = await conn.fetch(query, *params)
        return [ProductRead(**dict(r)) for r in rows]

    except asyncpg.PostgresError as e:
        logger.error("list_products: database error — %s", e)
        raise RuntimeError(f"Database error while listing products: {e}")


async def update_product(
    conn: asyncpg.Connection, 
    product_id: str, 
    data: ProductUpdate,
    updated_by: Optional[str] = None, 
    user_id: Optional[str] = None
) -> Optional[ProductRead]:
    try:
        query = """
            UPDATE products
            SET
                supplier_id  = COALESCE($1,  supplier_id),
                category_id  = COALESCE($2,  category_id),
                product_name = COALESCE($3,  product_name),
                description  = COALESCE($4,  description),
                sku          = COALESCE($5,  sku),
                price        = COALESCE($6,  price),
                cost_price   = COALESCE($7,  cost_price),
                weight       = COALESCE($8,  weight),
                status       = COALESCE($9,  status),
                updated_by   = $10,
                updated_at   = CURRENT_TIMESTAMP
            WHERE product_id = $11 AND deleted = FALSE
        """
        params = [
            data.supplier_id, 
            data.category_id, 
            data.product_name, 
            data.description,
            data.sku, 
            data.price, 
            data.cost_price, 
            data.weight, 
            data.status,
            updated_by, 
            product_id,
        ]
        if user_id:
            query += " AND user_id = $12"
            params.append(user_id)

        query += """
            RETURNING product_id, supplier_id, category_id, product_name, description,
                      sku, price, cost_price, weight, status,
                      user_id, created_at, updated_at, created_by, updated_by
        """
        row = await conn.fetchrow(query, *params)
        return ProductRead(**dict(row)) if row else None

    except asyncpg.UniqueViolationError:
        logger.warning("update_product(%s): duplicate SKU '%s'", product_id, data.sku)
        raise ValueError(f"A product with SKU '{data.sku}' already exists.")

    except asyncpg.ForeignKeyViolationError as e:
        logger.warning("update_product(%s): foreign key violation — %s", product_id, e)
        raise ValueError("Invalid supplier_id or category_id.")

    except asyncpg.PostgresError as e:
        logger.error("update_product(%s): database error — %s", product_id, e)
        raise RuntimeError(f"Database error while updating product: {e}")


async def delete_product(
    conn: asyncpg.Connection, 
    product_id: str, 
    deleted_by: Optional[str] = None,
    user_id: Optional[str] = None
) -> bool:
    try:
        query = """
            UPDATE products
            SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
            WHERE product_id = $1 AND deleted = FALSE
        """
        params = [product_id, deleted_by]
        if user_id:
            query += " AND user_id = $3"
            params.append(user_id)

        result = await conn.execute(query, *params)
        return result == "UPDATE 1"

    except asyncpg.PostgresError as e:
        logger.error("delete_product(%s): database error — %s", product_id, e)
        raise RuntimeError(f"Database error while deleting product: {e}")
