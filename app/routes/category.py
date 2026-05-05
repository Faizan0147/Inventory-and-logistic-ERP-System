from typing import Annotated

from fastapi import APIRouter, Depends, status
import asyncpg

from app.database import get_connection
from app.utils.dependencies import get_current_user
from app.dto.category import CategoryCreate, CategoryUpdate, CategoryRead
from app.controllers import category as category_controller

router = APIRouter()

Conn = Annotated[asyncpg.Connection, Depends(get_connection)]
CurrentUser = Annotated[dict, Depends(get_current_user)]


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(body: CategoryCreate, conn: Conn, current_user: CurrentUser):
    return await category_controller.create_category(conn, body, current_user)


@router.get("/", response_model=list[CategoryRead])
async def list_categories(
    conn: Conn, current_user: CurrentUser, offset: int = 0, limit: int = 100
):
    return await category_controller.list_categories(conn, offset, limit, current_user)


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: str, conn: Conn, current_user: CurrentUser):
    return await category_controller.get_category(conn, category_id, current_user)


@router.put("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: str, body: CategoryUpdate, conn: Conn, current_user: CurrentUser
):
    return await category_controller.update_category(
        conn, category_id, body, current_user
    )


@router.delete("/{category_id}", status_code=200)
async def delete_category(
    category_id: str, conn: Conn, current_user: CurrentUser
) -> dict:
    return await category_controller.delete_category(conn, category_id, current_user)
