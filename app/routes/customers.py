from typing import Annotated
from fastapi import APIRouter, Depends, status
import asyncpg

from app.database import get_connection
from app.utils.dependencies import get_current_user
from app.dto.customers import CustomerCreate, CustomerUpdate, CustomerRead
from app.controllers import customers as customer_controller

router = APIRouter()

Conn = Annotated[asyncpg.Connection, Depends(get_connection)]
CurrentUser = Annotated[dict, Depends(get_current_user)]


@router.post("/", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
async def create_customer(body: CustomerCreate, conn: Conn, current_user: CurrentUser):
    return await customer_controller.create_customer(conn, body, current_user)


@router.get("/", response_model=list[CustomerRead])
async def list_customers(conn: Conn, current_user: CurrentUser, offset: int = 0, limit: int = 100):
    return await customer_controller.list_customers(conn, offset, limit)


@router.get("/{customer_id}", response_model=CustomerRead)
async def get_customer(customer_id: str, conn: Conn, current_user: CurrentUser):
    return await customer_controller.get_customer(conn, customer_id)


@router.patch("/{customer_id}", response_model=CustomerRead)
async def update_customer(customer_id: str, body: CustomerUpdate, conn: Conn, current_user: CurrentUser):
    return await customer_controller.update_customer(conn, customer_id, body, current_user)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(customer_id: str, conn: Conn, current_user: CurrentUser):
    await customer_controller.delete_customer(conn, customer_id, current_user)