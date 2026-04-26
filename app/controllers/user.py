from fastapi import HTTPException
import asyncpg

from app.utils.security import hash_password
from app.dto.users import UserCreate, UserUpdate, UserRead
from app.repositories import users_repo


async def create_user(
    conn: asyncpg.Connection,
    body: UserCreate,
    current_user: dict,
) -> UserRead:
    hashed = hash_password(body.password)
    return await users_repo.create_user(
        conn, body, hashed, created_by=current_user["user_id"]
    )


async def list_users(
    conn: asyncpg.Connection, offset: int, limit: int, current_user: dict
) -> list[UserRead]:
    # SUPPLIER sees only their own record; ADMIN sees all
    current_user_id = current_user["user_id"] if current_user["role"] == "SUPPLIER" else None
    return await users_repo.list_users(conn, offset, limit)


async def get_user(
    conn: asyncpg.Connection, user_id: str, current_user: dict
) -> UserRead:
    # SUPPLIER can only fetch their own record
    current_user_id = current_user["user_id"] if current_user["role"] == "SUPPLIER" else None
    user = await users_repo.get_user(conn, user_id, current_user_id=current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def update_user(
    conn: asyncpg.Connection, user_id: str, body: UserUpdate, current_user: dict
) -> UserRead:
    # SUPPLIER can only update their own record
    current_user_id = current_user["user_id"] if current_user["role"] == "SUPPLIER" else None
    hashed = hash_password(body.password) if body.password else None
    user = await users_repo.update_user(
        conn, user_id, body,
        password_hash=hashed,
        updated_by=current_user["user_id"],
        current_user_id=current_user_id,
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def delete_user(
    conn: asyncpg.Connection, user_id: str, current_user: dict
) -> dict:
    # SUPPLIER can only delete their own record
    current_user_id = current_user["user_id"] if current_user["role"] == "SUPPLIER" else None
    deleted = await users_repo.delete_user(
        conn, user_id, deleted_by=current_user["user_id"], current_user_id=current_user_id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}
