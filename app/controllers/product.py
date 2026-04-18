from fastapi import HTTPException
import asyncpg

from app.dto.product import ProductRead, ProductCreate, ProductUpdate
from app.repositories import product_repo


async def create_product(
    conn: asyncpg.Connection,
    body: ProductCreate,
    current_user: dict,
) -> ProductRead:
    return await product_repo.create_product(
        conn, body, created_by=current_user["user_id"]
    )


async def get_product(
    conn: asyncpg.Connection, product_id: str
) -> ProductRead:
    product = await product_repo.get_product(conn, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="product not found")
    return product


async def list_products(
    conn: asyncpg.Connection, offset: int, limit: int
) -> list[ProductRead]:
    return await product_repo.list_products(conn, offset, limit)


async def update_product(
    conn: asyncpg.Connection,
    product_id: str,
    body: ProductUpdate,
    current_user: dict,
) -> ProductRead:
    product = await product_repo.update_product(
        conn, product_id, body, updated_by=current_user["user_id"]
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


async def delete_product(
    conn: asyncpg.Connection, product_id: str, current_user: dict
) -> None:
    deleted = await product_repo.delete_product(
        conn, product_id, deleted_by=current_user["user_id"]
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")