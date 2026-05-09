from __future__ import annotations

import asyncpg
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from app.dto.reports import (
    CategoriesReportResponse,
    CategoriesReportRow,
    CategoriesReportSummary,
    InventoryReportResponse,
    InventoryReportRow,
    InventoryReportSummary,
    InvoiceItemsReportResponse,
    InvoiceItemsReportRow,
    InvoiceItemsReportSummary,
    InvoicesReportResponse,
    InvoicesReportRow,
    InvoicesReportSummary,
    PurchaseOrderItemsReportResponse,
    PurchaseOrderItemsReportRow,
    PurchaseOrderItemsReportSummary,
    PurchaseOrdersReportResponse,
    PurchaseOrdersReportRow,
    PurchaseOrdersReportSummary,
    ProductsReportResponse,
    ProductsReportRow,
    ProductsReportSummary,
    ShipmentsReportResponse,
    ShipmentsReportRow,
    ShipmentsReportSummary,
    UsersReportResponse,
    UsersReportRow,
    UsersReportSummary,
)
from app.repositories import reports_repo
from app.utils.csv_export import build_csv_stream_response


def _get_scope_user_id(current_user: dict) -> str | None:
    return current_user["user_id"] if current_user.get("role") == "SUPPLIER" else None


def _handle_db_error(exc: Exception) -> None:
    raise HTTPException(
        status_code=500, detail=f"Database error while fetching report data: {str(exc)}"
    )


async def get_users_report(conn: asyncpg.Connection, current_user: dict) -> UsersReportResponse:
    scoped_user = _get_scope_user_id(current_user)
    try:
        summary = await reports_repo.get_users_summary(conn, scoped_user)
        rows = await reports_repo.get_users_rows(conn, scoped_user)
    except asyncpg.PostgresError as exc:
        _handle_db_error(exc)

    return UsersReportResponse(
        summary=UsersReportSummary(**summary),
        rows=[UsersReportRow(**row) for row in rows],
    )


async def export_users_csv(conn: asyncpg.Connection, current_user: dict) -> StreamingResponse:
    scoped_user = _get_scope_user_id(current_user)
    try:
        rows = await reports_repo.get_users_rows(conn, scoped_user)
    except asyncpg.PostgresError as exc:
        _handle_db_error(exc)
    columns = [
        ("User ID", "user_id"),
        ("Name", "name"),
        ("Email", "email"),
        ("Role", "role"),
        ("Status", "status"),
        ("Created At", "created_at"),
    ]
    return build_csv_stream_response(rows=rows, columns=columns, filename_prefix="users")


async def get_categories_report(
    conn: asyncpg.Connection, current_user: dict
) -> CategoriesReportResponse:
    scoped_user = _get_scope_user_id(current_user)
    try:
        summary = await reports_repo.get_categories_summary(conn, scoped_user)
        rows = await reports_repo.get_categories_rows(conn, scoped_user)
    except asyncpg.PostgresError as exc:
        _handle_db_error(exc)
    return CategoriesReportResponse(
        summary=CategoriesReportSummary(**summary),
        rows=[CategoriesReportRow(**row) for row in rows],
    )


async def export_categories_csv(
    conn: asyncpg.Connection, current_user: dict
) -> StreamingResponse:
    scoped_user = _get_scope_user_id(current_user)
    try:
        rows = await reports_repo.get_categories_rows(conn, scoped_user)
    except asyncpg.PostgresError as exc:
        _handle_db_error(exc)
    columns = [
        ("Category ID", "category_id"),
        ("Category Name", "category_name"),
        ("Parent Category", "parent_category"),
        ("Product Count", "product_count"),
        ("Created At", "created_at"),
    ]
    return build_csv_stream_response(rows=rows, columns=columns, filename_prefix="categories")


async def get_products_report(
    conn: asyncpg.Connection, current_user: dict
) -> ProductsReportResponse:
    scoped_user = _get_scope_user_id(current_user)
    try:
        summary = await reports_repo.get_products_summary(conn, scoped_user)
        rows = await reports_repo.get_products_rows(conn, scoped_user)
    except asyncpg.PostgresError as exc:
        _handle_db_error(exc)
    return ProductsReportResponse(
        summary=ProductsReportSummary(**summary),
        rows=[ProductsReportRow(**row) for row in rows],
    )


async def export_products_csv(conn: asyncpg.Connection, current_user: dict) -> StreamingResponse:
    scoped_user = _get_scope_user_id(current_user)
    try:
        rows = await reports_repo.get_products_rows(conn, scoped_user)
    except asyncpg.PostgresError as exc:
        _handle_db_error(exc)
    columns = [
        ("Product ID", "product_id"),
        ("Product Name", "product_name"),
        ("SKU", "sku"),
        ("Supplier", "supplier"),
        ("Category", "category"),
        ("Price", "price"),
        ("Cost Price", "cost_price"),
        ("Status", "status"),
        ("Created At", "created_at"),
    ]
    return build_csv_stream_response(rows=rows, columns=columns, filename_prefix="products")


async def get_inventory_report(
    conn: asyncpg.Connection, current_user: dict
) -> InventoryReportResponse:
    scoped_user = _get_scope_user_id(current_user)
    try:
        summary = await reports_repo.get_inventory_summary(conn, scoped_user)
        rows = await reports_repo.get_inventory_rows(conn, scoped_user)
    except asyncpg.PostgresError as exc:
        _handle_db_error(exc)
    return InventoryReportResponse(
        summary=InventoryReportSummary(**summary),
        rows=[InventoryReportRow(**row) for row in rows],
    )


async def export_inventory_csv(conn: asyncpg.Connection, current_user: dict) -> StreamingResponse:
    scoped_user = _get_scope_user_id(current_user)
    try:
        rows = await reports_repo.get_inventory_rows(conn, scoped_user)
    except asyncpg.PostgresError as exc:
        _handle_db_error(exc)
    columns = [
        ("Product", "product"),
        ("Warehouse", "warehouse"),
        ("Quantity", "quantity"),
        ("Reorder Level", "reorder_level"),
        ("Last Restocked", "last_restocked"),
        ("Updated At", "updated_at"),
    ]
    return build_csv_stream_response(rows=rows, columns=columns, filename_prefix="inventory")


async def get_purchase_orders_report(
    conn: asyncpg.Connection, current_user: dict
) -> PurchaseOrdersReportResponse:
    scoped_user = _get_scope_user_id(current_user)
    try:
        summary = await reports_repo.get_purchase_orders_summary(conn, scoped_user)
        rows = await reports_repo.get_purchase_orders_rows(conn, scoped_user)
    except asyncpg.PostgresError as exc:
        _handle_db_error(exc)
    return PurchaseOrdersReportResponse(
        summary=PurchaseOrdersReportSummary(**summary),
        rows=[PurchaseOrdersReportRow(**row) for row in rows],
    )


async def export_purchase_orders_csv(
    conn: asyncpg.Connection, current_user: dict
) -> StreamingResponse:
    scoped_user = _get_scope_user_id(current_user)
    try:
        rows = await reports_repo.get_purchase_orders_rows(conn, scoped_user)
    except asyncpg.PostgresError as exc:
        _handle_db_error(exc)
    columns = [
        ("PO Number", "po_number"),
        ("Supplier", "supplier"),
        ("Warehouse", "warehouse"),
        ("Order Date", "order_date"),
        ("Expected Delivery", "expected_delivery"),
        ("Total Amount", "total_amount"),
        ("Status", "status"),
    ]
    return build_csv_stream_response(
        rows=rows, columns=columns, filename_prefix="purchase-orders"
    )


async def get_purchase_order_items_report(
    conn: asyncpg.Connection, current_user: dict
) -> PurchaseOrderItemsReportResponse:
    scoped_user = _get_scope_user_id(current_user)
    try:
        summary = await reports_repo.get_purchase_order_items_summary(conn, scoped_user)
        rows = await reports_repo.get_purchase_order_items_rows(conn, scoped_user)
    except asyncpg.PostgresError as exc:
        _handle_db_error(exc)
    return PurchaseOrderItemsReportResponse(
        summary=PurchaseOrderItemsReportSummary(**summary),
        rows=[PurchaseOrderItemsReportRow(**row) for row in rows],
    )


async def export_purchase_order_items_csv(
    conn: asyncpg.Connection, current_user: dict
) -> StreamingResponse:
    scoped_user = _get_scope_user_id(current_user)
    try:
        rows = await reports_repo.get_purchase_order_items_rows(conn, scoped_user)
    except asyncpg.PostgresError as exc:
        _handle_db_error(exc)
    columns = [
        ("PO Item ID", "po_item_id"),
        ("PO Number", "po_number"),
        ("Product", "product"),
        ("Quantity", "quantity"),
        ("Price", "price"),
        ("Total", "total"),
    ]
    return build_csv_stream_response(
        rows=rows, columns=columns, filename_prefix="purchase-order-items"
    )


async def get_invoices_report(
    conn: asyncpg.Connection, current_user: dict
) -> InvoicesReportResponse:
    scoped_user = _get_scope_user_id(current_user)
    try:
        summary = await reports_repo.get_invoices_summary(conn, scoped_user)
        rows = await reports_repo.get_invoices_rows(conn, scoped_user)
    except asyncpg.PostgresError as exc:
        _handle_db_error(exc)
    return InvoicesReportResponse(
        summary=InvoicesReportSummary(**summary),
        rows=[InvoicesReportRow(**row) for row in rows],
    )


async def export_invoices_csv(conn: asyncpg.Connection, current_user: dict) -> StreamingResponse:
    scoped_user = _get_scope_user_id(current_user)
    try:
        rows = await reports_repo.get_invoices_rows(conn, scoped_user)
    except asyncpg.PostgresError as exc:
        _handle_db_error(exc)
    columns = [
        ("Invoice Number", "invoice_number"),
        ("Supplier", "supplier"),
        ("PO Number", "po_number"),
        ("Invoice Date", "invoice_date"),
        ("Total Amount", "total_amount"),
        ("Status", "status"),
    ]
    return build_csv_stream_response(rows=rows, columns=columns, filename_prefix="invoices")


async def get_invoice_items_report(
    conn: asyncpg.Connection, current_user: dict
) -> InvoiceItemsReportResponse:
    scoped_user = _get_scope_user_id(current_user)
    try:
        summary = await reports_repo.get_invoice_items_summary(conn, scoped_user)
        rows = await reports_repo.get_invoice_items_rows(conn, scoped_user)
    except asyncpg.PostgresError as exc:
        _handle_db_error(exc)
    return InvoiceItemsReportResponse(
        summary=InvoiceItemsReportSummary(**summary),
        rows=[InvoiceItemsReportRow(**row) for row in rows],
    )


async def export_invoice_items_csv(
    conn: asyncpg.Connection, current_user: dict
) -> StreamingResponse:
    scoped_user = _get_scope_user_id(current_user)
    try:
        rows = await reports_repo.get_invoice_items_rows(conn, scoped_user)
    except asyncpg.PostgresError as exc:
        _handle_db_error(exc)
    columns = [
        ("Invoice Item ID", "invoice_item_id"),
        ("Invoice Number", "invoice_number"),
        ("Product", "product"),
        ("Quantity", "quantity"),
        ("Price", "price"),
        ("Total", "total"),
    ]
    return build_csv_stream_response(
        rows=rows, columns=columns, filename_prefix="invoice-items"
    )


async def get_shipments_report(
    conn: asyncpg.Connection, current_user: dict
) -> ShipmentsReportResponse:
    scoped_user = _get_scope_user_id(current_user)
    try:
        summary = await reports_repo.get_shipments_summary(conn, scoped_user)
        rows = await reports_repo.get_shipments_rows(conn, scoped_user)
    except asyncpg.PostgresError as exc:
        _handle_db_error(exc)
    return ShipmentsReportResponse(
        summary=ShipmentsReportSummary(**summary),
        rows=[ShipmentsReportRow(**row) for row in rows],
    )


async def export_shipments_csv(conn: asyncpg.Connection, current_user: dict) -> StreamingResponse:
    scoped_user = _get_scope_user_id(current_user)
    try:
        rows = await reports_repo.get_shipments_rows(conn, scoped_user)
    except asyncpg.PostgresError as exc:
        _handle_db_error(exc)
    columns = [
        ("Shipment ID", "shipment_id"),
        ("Tracking Number", "tracking_number"),
        ("Carrier", "carrier"),
        ("Shipment Date", "shipment_date"),
        ("Estimated Arrival", "estimated_arrival"),
        ("Status", "status"),
    ]
    return build_csv_stream_response(rows=rows, columns=columns, filename_prefix="shipments")
