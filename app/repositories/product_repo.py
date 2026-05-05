import logging
from uuid import uuid4
from typing import Optional
import asyncpg

from app.dto.product import (
    ProductCreate,
    ProductRead,
    ProductUpdate,
    SupplierSummary,
    CategorySummary,
)

logger = logging.getLogger(__name__)

_SELECT = """
    SELECT
        p.product_id, p.supplier_id, p.user_id, p.category_id,
        p.product_name, p.description, p.sku, p.price, p.cost_price,
        p.weight, p.status, p.created_at, p.updated_at, p.created_by, p.updated_by,
        s.supplier_name, s.contact_email, s.contact_phone,
        c.category_name, c.description AS category_description
    FROM products p
    LEFT JOIN suppliers s ON s.supplier_id = p.supplier_id AND s.deleted = FALSE
    LEFT JOIN categories c ON c.category_id = p.category_id AND c.deleted = FALSE
"""


def _build(row: asyncpg.Record) -> ProductRead:
    d = dict(row)
    supplier = None
    if d.get("supplier_name"):
        supplier = SupplierSummary(
            supplier_id=d["supplier_id"],
            supplier_name=d["supplier_name"],
            contact_email=d.get("contact_email"),
            contact_phone=d.get("contact_phone"),
        )
    category = None
    if d.get("category_name"):
        category = CategorySummary(
            category_id=d["category_id"],
            category_name=d["category_name"],
            description=d.get("category_description"),
        )
    return ProductRead(
        product_id=d["product_id"],
        supplier_id=d["supplier_id"],
        user_id=d["user_id"],
        category_id=d.get("category_id"),
        product_name=d["product_name"],
        description=d.get("description"),
        sku=d["sku"],
        price=d.get("price"),
        cost_price=d.get("cost_price"),
        weight=d.get("weight"),
        status=d["status"],
        supplier=supplier,
        category=category,
        created_at=d.get("created_at"),
        updated_at=d.get("updated_at"),
        created_by=d.get("created_by"),
        updated_by=d.get("updated_by"),
    )


async def create_product(
    conn: asyncpg.Connection,
    data: ProductCreate,
    user_id: str,
    created_by: Optional[str] = None,
) -> ProductRead:
    try:
        row = await conn.fetchrow(
            """
            INSERT INTO products (
                product_id, supplier_id, user_id, category_id, product_name, description,
                sku, price, cost_price, weight, status, created_by, updated_by
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $12)
            RETURNING product_id
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
        return await get_product(conn, row["product_id"])

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
    user_id: Optional[str] = None,
) -> Optional[ProductRead]:
    try:
        query = _SELECT + " WHERE p.product_id = $1 AND p.deleted = FALSE"
        params = [product_id]
        if user_id:
            query += " AND p.user_id = $2"
            params.append(user_id)
        row = await conn.fetchrow(query, *params)
        return _build(row) if row else None
    except asyncpg.PostgresError as e:
        logger.error("get_product(%s): database error — %s", product_id, e)
        raise RuntimeError(f"Database error while fetching product: {e}")


async def list_products(
    conn: asyncpg.Connection,
    offset: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
) -> list[ProductRead]:
    try:
        query = _SELECT + " WHERE p.deleted = FALSE"
        params = [limit, offset]
        if user_id:
            query += " AND p.user_id = $3"
            params.append(user_id)
        query += " ORDER BY p.product_name LIMIT $1 OFFSET $2"
        rows = await conn.fetch(query, *params)
        return [_build(r) for r in rows]
    except asyncpg.PostgresError as e:
        logger.error("list_products: database error — %s", e)
        raise RuntimeError(f"Database error while listing products: {e}")


async def update_product(
    conn: asyncpg.Connection,
    product_id: str,
    data: ProductUpdate,
    updated_by: Optional[str] = None,
    user_id: Optional[str] = None,
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
        query += " RETURNING product_id"
        row = await conn.fetchrow(query, *params)
        if not row:
            return None
        return await get_product(conn, row["product_id"])

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
    user_id: Optional[str] = None,
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
