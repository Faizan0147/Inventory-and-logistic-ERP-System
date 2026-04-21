from fastapi import HTTPException
import asyncpg

from app.dto.product import ProductRead, ProductCreate, ProductUpdate
from app.repositories import product_repo


async def create_product(
    conn: asyncpg.Connection,
    body: ProductCreate,
    current_user: dict,
) -> ProductRead:
    # If the user is a SUPPLIER, ensure they are creating a product for themselves
    if current_user["role"] == "SUPPLIER" and body.supplier_id != current_user["supplier_id"]:
         raise HTTPException(status_code=403, detail="Suppliers can only create products for themselves")
         
    return await product_repo.create_product(
        conn, body, created_by=current_user["user_id"]
    )


async def get_product(
    conn: asyncpg.Connection, product_id: str, current_user: dict
) -> ProductRead:
    supplier_id = current_user["supplier_id"] if current_user["role"] == "SUPPLIER" else None
    product = await product_repo.get_product(conn, product_id, supplier_id=supplier_id)
    if not product:
        raise HTTPException(status_code=404, detail="product not found")
    return product


async def list_products(
    conn: asyncpg.Connection, offset: int, limit: int, current_user: dict
) -> list[ProductRead]:
    supplier_id = current_user["supplier_id"] if current_user["role"] == "SUPPLIER" else None
    return await product_repo.list_products(conn, offset, limit, supplier_id=supplier_id)


async def update_product(
    conn: asyncpg.Connection,
    product_id: str,
    body: ProductUpdate,
    current_user: dict,
) -> ProductRead:
    supplier_id = current_user["supplier_id"] if current_user["role"] == "SUPPLIER" else None
    
    # If a supplier tries to update and changes the supplier_id, block it
    if current_user["role"] == "SUPPLIER" and body.supplier_id and body.supplier_id != current_user["supplier_id"]:
        raise HTTPException(status_code=403, detail="Cannot change supplier assignment")

    product = await product_repo.update_product(
        conn, product_id, body, updated_by=current_user["user_id"], supplier_id=supplier_id
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


async def delete_product(
    conn: asyncpg.Connection, product_id: str, current_user: dict
) -> None:
    supplier_id = current_user["supplier_id"] if current_user["role"] == "SUPPLIER" else None
    deleted = await product_repo.delete_product(
        conn, product_id, deleted_by=current_user["user_id"], supplier_id=supplier_id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found or access denied")