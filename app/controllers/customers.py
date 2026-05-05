import logging
from fastapi import HTTPException
import asyncpg

from app.dto.customers import CustomerCreate, CustomerUpdate, CustomerRead
from app.repositories import customer_repo

logger = logging.getLogger(__name__)


def _get_current_user(current_user: dict) -> str | None:
    return current_user["user_id"] if current_user["role"] == "SUPPLIER" else None


async def create_customer(
    conn: asyncpg.Connection,
    data: CustomerCreate,
    current_user: dict,
) -> CustomerRead:

    try:
        return await customer_repo.create_customer(
            conn,
            data,
            user_id=current_user["user_id"],
            created_by=current_user["user_id"],
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    except RuntimeError as e:
        logger.error(
            "create_customer failed for user %s: %s", current_user["user_id"], e
        )
        raise HTTPException(status_code=500, detail=str(e))


async def get_customer(
    conn: asyncpg.Connection,
    customer_id: str,
    current_user: dict,
) -> CustomerRead:

    try:
        customer = await customer_repo.get_customer(
            conn, customer_id, user_id=_get_current_user(current_user)
        )

    except RuntimeError as e:
        logger.error(
            "get_customer(%s) failed for user %s: %s",
            customer_id,
            current_user["user_id"],
            e,
        )
        raise HTTPException(status_code=500, detail=str(e))

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


async def list_customers(
    conn: asyncpg.Connection,
    offset: int,
    limit: int,
    current_user: dict,
) -> list[CustomerRead]:

    try:
        return await customer_repo.list_customers(
            conn, offset, limit, user_id=_get_current_user(current_user)
        )

    except RuntimeError as e:
        logger.error(
            "list_customers failed for user %s: %s", current_user["user_id"], e
        )
        raise HTTPException(status_code=500, detail=str(e))


async def update_customer(
    conn: asyncpg.Connection,
    customer_id: str,
    data: CustomerUpdate,
    current_user: dict,
) -> CustomerRead:

    try:
        customer = await customer_repo.update_customer(
            conn,
            customer_id,
            data,
            updated_by=current_user["user_id"],
            user_id=_get_current_user(current_user),
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    except RuntimeError as e:
        logger.error(
            "update_customer(%s) failed for user %s: %s",
            customer_id,
            current_user["user_id"],
            e,
        )
        raise HTTPException(status_code=500, detail=str(e))

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


async def delete_customer(
    conn: asyncpg.Connection,
    customer_id: str,
    current_user: dict,
) -> dict:

    try:
        deleted = await customer_repo.delete_customer(
            conn,
            customer_id,
            deleted_by=current_user["user_id"],
            user_id=_get_current_user(current_user),
        )

    except RuntimeError as e:
        logger.error(
            "delete_customer(%s) failed for user %s: %s",
            customer_id,
            current_user["user_id"],
            e,
        )
        raise HTTPException(status_code=500, detail=str(e))

    if not deleted:
        raise HTTPException(status_code=404, detail="Customer not found")

    return {"message": "Customer deleted successfully"}
