from uuid import uuid4
from typing import Optional
import asyncpg

from app.dto.product import (
    ProductCreate,
    ProductRead,
    ProductUpdate
)


async def create_product(
    conn: asyncpg.Connection, data: ProductCreate, created_by: Optional[str] = None
) -> ProductRead:
    row = await conn.fetchrow(
        """
        INSERT INTO products (product_id, supplier_id, category_id, product_name, description, sku, price, cost_price, weight, status, created_by, updated_by)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $11)
        RETURNING product_id, supplier_id, category_id, product_name, description, sku, price, cost_price, weight, status,
                  created_at, updated_at, created_by, updated_by
        """,
        str(uuid4()), data.supplier_id, data.category_id, data.product_name,
        data.description, data.sku, data.price, data.cost_price, data.weight,
        data.status, created_by,
    )
    return ProductRead(**dict(row))


async def get_product(conn: asyncpg.Connection, product_id: str, supplier_id: Optional[str] = None) -> Optional[ProductRead]:
    query = """
        SELECT product_id, supplier_id, category_id, product_name, description, sku, price, cost_price, weight, status,
               created_at, updated_at, created_by, updated_by
        FROM products
        WHERE product_id = $1 AND deleted = FALSE
    """
    params = [product_id]
    if supplier_id:
        query += " AND supplier_id = $2"
        params.append(supplier_id)
        
    row = await conn.fetchrow(query, *params)
    if not row:
        return None
    return ProductRead(**dict(row))


async def list_products(
    conn: asyncpg.Connection, offset: int = 0, limit: int = 100, supplier_id: Optional[str] = None
) -> list[ProductRead]:
    query = """
        SELECT product_id, supplier_id, category_id, product_name, description, sku, price, cost_price, weight, status,
               created_at, updated_at, created_by, updated_by
        FROM products
        WHERE deleted = FALSE
    """
    params = [limit, offset]
    if supplier_id:
        query += " AND supplier_id = $3"
        params.append(supplier_id)
        
    query += " ORDER BY product_name LIMIT $1 OFFSET $2"
    
    rows = await conn.fetch(query, *params)
    return [ProductRead(**dict(r)) for r in rows]


async def update_product(
    conn: asyncpg.Connection, product_id: str, data: ProductUpdate, updated_by: Optional[str] = None, supplier_id: Optional[str] = None
) -> Optional[ProductRead]:
    query = """
        UPDATE products
        SET
            supplier_id = COALESCE($1, supplier_id),
            category_id = COALESCE($2, category_id),
            product_name = COALESCE($3, product_name),
            description = COALESCE($4, description),
            sku = COALESCE($5, sku),
            price = COALESCE($6, price),
            cost_price = COALESCE($7, cost_price),
            weight = COALESCE($8, weight),
            status = COALESCE($9, status),
            updated_by = $10,
            updated_at = CURRENT_TIMESTAMP
        WHERE product_id = $11 AND deleted = FALSE
    """
    params = [
        data.supplier_id, data.category_id, data.product_name, data.description,
        data.sku, data.price, data.cost_price, data.weight, data.status,
        updated_by, product_id
    ]
    if supplier_id:
        query = query.replace("WHERE product_id = $11", "WHERE product_id = $11 AND supplier_id = $12")
        params.append(supplier_id)

    query += " RETURNING product_id, supplier_id, category_id, product_name, description, sku, price, cost_price, weight, status, created_at, updated_at, created_by, updated_by"
    
    row = await conn.fetchrow(query, *params)
    return ProductRead(**dict(row)) if row else None


async def delete_product(
    conn: asyncpg.Connection, product_id: str, deleted_by: Optional[str] = None, supplier_id: Optional[str] = None
) -> bool:
    query = """
        UPDATE products
        SET deleted = TRUE, updated_at = CURRENT_TIMESTAMP, updated_by = $2
        WHERE product_id = $1 AND deleted = FALSE
    """
    params = [product_id, deleted_by]
    if supplier_id:
        query += " AND supplier_id = $3"
        params.append(supplier_id)
        
    result = await conn.execute(query, *params)
    return result == "UPDATE 1"