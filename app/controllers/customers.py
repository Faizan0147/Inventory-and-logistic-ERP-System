from fastapi import HTTPException
import asyncpg

from app.dto.customers import CustomerCreate, CustomerUpdate, CustomerRead
from app.repositories import customer_repo


async def create_customer(
    conn: asyncpg.Connection,
    data: CustomerCreate,
    current_user: dict,
) -> CustomerRead:
    return await customer_repo.create_customer(
        conn, data, created_by=current_user["user_id"]
    )


async def list_customers(
    conn: asyncpg.Connection, offset: int, limit: int
) -> list[CustomerRead]:
    return await customer_repo.list_customers(conn, offset, limit)


async def get_customer(
    conn: asyncpg.Connection, customer_id: str
) -> CustomerRead:
    customer = await customer_repo.get_customer(conn, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


async def update_customer(
    conn: asyncpg.Connection,
    customer_id: str,
    data: CustomerUpdate,
    current_user: dict,
) -> CustomerRead:
    customer = await customer_repo.update_customer(
        conn, customer_id, data, updated_by=current_user["user_id"]
    )
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


async def delete_customer(
    conn: asyncpg.Connection, customer_id: str, current_user: dict
) -> None:
    deleted = await customer_repo.delete_customer(
        conn, customer_id, deleted_by=current_user["user_id"]
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Customer not found")