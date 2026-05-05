from typing import Annotated

from fastapi import APIRouter, Depends, status
import asyncpg

from app.database import get_connection
from app.utils.dependencies import get_current_user, require_role
from app.dto.users import UserCreate, UserUpdate, UserRead
from app.controllers import user as user_controller

router = APIRouter()


Conn = Annotated[asyncpg.Connection, Depends(get_connection)]
CurrentUser = Annotated[dict, Depends(get_current_user)]


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("SUPERADMIN"))],
)
async def create_user(body: UserCreate, conn: Conn, current_user: CurrentUser):
    return await user_controller.create_user(conn, body, current_user)


@router.get(
    "/",
    response_model=list[UserRead],
    dependencies=[Depends(require_role("SUPERADMIN"))],
)
async def list_users(
    conn: Conn, current_user: CurrentUser, offset: int = 0, limit: int = 100
):
    return await user_controller.list_users(
        conn, offset, limit, current_user=current_user
    )


@router.get(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(require_role("SUPERADMIN"))],
)
async def get_user(user_id: str, conn: Conn, current_user: CurrentUser):
    return await user_controller.get_user(conn, user_id, current_user=current_user)


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str, body: UserUpdate, conn: Conn, current_user: CurrentUser
):
    return await user_controller.update_user(conn, user_id, body, current_user)


@router.delete("/{user_id}", status_code=200)
async def delete_user(user_id: str, conn: Conn, current_user: CurrentUser) -> dict:
    return await user_controller.delete_user(conn, user_id, current_user)
