from typing import Annotated

import asyncpg
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.controllers import reports as reports_controller
from app.database import get_connection
from app.dto.reports import (
    CategoriesReportResponse,
    InventoryReportResponse,
    InvoiceItemsReportResponse,
    InvoicesReportResponse,
    PurchaseOrderItemsReportResponse,
    PurchaseOrdersReportResponse,
    ProductsReportResponse,
    ShipmentsReportResponse,
    UsersReportResponse,
)
from app.utils.dependencies import get_current_user

router = APIRouter()

Conn = Annotated[asyncpg.Connection, Depends(get_connection)]
CurrentUser = Annotated[dict, Depends(get_current_user)]


@router.get("/users", response_model=UsersReportResponse)
async def get_users_report(conn: Conn, current_user: CurrentUser):
    return await reports_controller.get_users_report(conn, current_user)


@router.get("/users/summary")
async def get_users_summary(conn: Conn, current_user: CurrentUser):
    response = await reports_controller.get_users_report(conn, current_user)
    return response.summary


@router.get("/users/export/csv", response_class=StreamingResponse)
async def export_users_csv(conn: Conn, current_user: CurrentUser):
    return await reports_controller.export_users_csv(conn, current_user)


@router.get("/categories", response_model=CategoriesReportResponse)
async def get_categories_report(conn: Conn, current_user: CurrentUser):
    return await reports_controller.get_categories_report(conn, current_user)


@router.get("/categories/summary")
async def get_categories_summary(conn: Conn, current_user: CurrentUser):
    response = await reports_controller.get_categories_report(conn, current_user)
    return response.summary


@router.get("/categories/export/csv", response_class=StreamingResponse)
async def export_categories_csv(conn: Conn, current_user: CurrentUser):
    return await reports_controller.export_categories_csv(conn, current_user)


@router.get("/products", response_model=ProductsReportResponse)
async def get_products_report(conn: Conn, current_user: CurrentUser):
    return await reports_controller.get_products_report(conn, current_user)


@router.get("/products/summary")
async def get_products_summary(conn: Conn, current_user: CurrentUser):
    response = await reports_controller.get_products_report(conn, current_user)
    return response.summary


@router.get("/products/export/csv", response_class=StreamingResponse)
async def export_products_csv(conn: Conn, current_user: CurrentUser):
    return await reports_controller.export_products_csv(conn, current_user)


@router.get("/inventory", response_model=InventoryReportResponse)
async def get_inventory_report(conn: Conn, current_user: CurrentUser):
    return await reports_controller.get_inventory_report(conn, current_user)


@router.get("/inventory/summary")
async def get_inventory_summary(conn: Conn, current_user: CurrentUser):
    response = await reports_controller.get_inventory_report(conn, current_user)
    return response.summary


@router.get("/inventory/export/csv", response_class=StreamingResponse)
async def export_inventory_csv(conn: Conn, current_user: CurrentUser):
    return await reports_controller.export_inventory_csv(conn, current_user)


@router.get("/purchase-orders", response_model=PurchaseOrdersReportResponse)
async def get_purchase_orders_report(conn: Conn, current_user: CurrentUser):
    return await reports_controller.get_purchase_orders_report(conn, current_user)


@router.get("/purchase-orders/summary")
async def get_purchase_orders_summary(conn: Conn, current_user: CurrentUser):
    response = await reports_controller.get_purchase_orders_report(conn, current_user)
    return response.summary


@router.get("/purchase-orders/export/csv", response_class=StreamingResponse)
async def export_purchase_orders_csv(conn: Conn, current_user: CurrentUser):
    return await reports_controller.export_purchase_orders_csv(conn, current_user)


@router.get("/purchase-order-items", response_model=PurchaseOrderItemsReportResponse)
async def get_purchase_order_items_report(conn: Conn, current_user: CurrentUser):
    return await reports_controller.get_purchase_order_items_report(conn, current_user)


@router.get("/purchase-order-items/summary")
async def get_purchase_order_items_summary(conn: Conn, current_user: CurrentUser):
    response = await reports_controller.get_purchase_order_items_report(conn, current_user)
    return response.summary


@router.get("/purchase-order-items/export/csv", response_class=StreamingResponse)
async def export_purchase_order_items_csv(conn: Conn, current_user: CurrentUser):
    return await reports_controller.export_purchase_order_items_csv(conn, current_user)


@router.get("/invoices", response_model=InvoicesReportResponse)
async def get_invoices_report(conn: Conn, current_user: CurrentUser):
    return await reports_controller.get_invoices_report(conn, current_user)


@router.get("/invoices/summary")
async def get_invoices_summary(conn: Conn, current_user: CurrentUser):
    response = await reports_controller.get_invoices_report(conn, current_user)
    return response.summary


@router.get("/invoices/export/csv", response_class=StreamingResponse)
async def export_invoices_csv(conn: Conn, current_user: CurrentUser):
    return await reports_controller.export_invoices_csv(conn, current_user)


@router.get("/invoice-items", response_model=InvoiceItemsReportResponse)
async def get_invoice_items_report(conn: Conn, current_user: CurrentUser):
    return await reports_controller.get_invoice_items_report(conn, current_user)


@router.get("/invoice-items/summary")
async def get_invoice_items_summary(conn: Conn, current_user: CurrentUser):
    response = await reports_controller.get_invoice_items_report(conn, current_user)
    return response.summary


@router.get("/invoice-items/export/csv", response_class=StreamingResponse)
async def export_invoice_items_csv(conn: Conn, current_user: CurrentUser):
    return await reports_controller.export_invoice_items_csv(conn, current_user)


@router.get("/shipments", response_model=ShipmentsReportResponse)
async def get_shipments_report(conn: Conn, current_user: CurrentUser):
    return await reports_controller.get_shipments_report(conn, current_user)


@router.get("/shipments/summary")
async def get_shipments_summary(conn: Conn, current_user: CurrentUser):
    response = await reports_controller.get_shipments_report(conn, current_user)
    return response.summary


@router.get("/shipments/export/csv", response_class=StreamingResponse)
async def export_shipments_csv(conn: Conn, current_user: CurrentUser):
    return await reports_controller.export_shipments_csv(conn, current_user)
