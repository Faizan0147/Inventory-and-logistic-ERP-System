from typing import Annotated

from fastapi import APIRouter, Depends, status
import asyncpg

from app.database import get_connection
from app.utils.dependencies import get_current_user
from app.dto.product import ProductCreate, ProductRead, ProductUpdate
from app.controllers import product as product_controller

router = APIRouter()

Conn = Annotated[asyncpg.Connection, Depends(get_connection)]
CurrentUser = Annotated[dict, Depends(get_current_user)]


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(body: ProductCreate, conn: Conn, current_user: CurrentUser):
    return await product_controller.create_product(conn, body, current_user)


@router.get("/", response_model=list[ProductRead])
async def list_products(conn: Conn, current_user: CurrentUser, offset: int = 0, limit: int = 100):
    return await product_controller.list_products(conn, offset, limit, current_user=current_user)


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: str, conn: Conn, current_user: CurrentUser):
    return await product_controller.get_product(conn, product_id, current_user=current_user)



@router.put("/{product_id}", response_model=ProductRead)
async def update_product(product_id: str, body: ProductUpdate, conn: Conn, current_user: CurrentUser):
    return await product_controller.update_product(conn, product_id, body, current_user)


@router.delete("/{product_id}", status_code=200)
async def delete_product(product_id: str, conn: Conn, current_user: CurrentUser) -> dict:
    return await product_controller.delete_product(conn, product_id, current_user)