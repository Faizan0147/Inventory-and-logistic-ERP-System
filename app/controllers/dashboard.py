"""
Dashboard controller: business logic for SUPERADMIN and SUPPLIER dashboards.
"""

import asyncpg
from fastapi import HTTPException

from app.dto.dashboard import (
    SuperAdminDashboard,
    SupplierDashboard,
    SuperAdminCards,
    SupplierCards,
    SuperAdminCharts,
    SupplierCharts,
    RevenueTrendItem,
    OrderStatusItem,
    TopSupplierItem,
    SalesTrendItem,
    TopProductItem,
)
from app.repositories import dashboard_repo


async def get_dashboard(
    conn: asyncpg.Connection, current_user: dict
) -> SuperAdminDashboard | SupplierDashboard:
    """
    Get dashboard data based on user role.
    Returns different dashboard structure for SUPERADMIN vs SUPPLIER.
    """
    role = current_user.get("role")
    user_id = current_user.get("user_id")

    if role == "SUPERADMIN":
        return await _get_superadmin_dashboard(conn)
    elif role == "SUPPLIER":
        return await _get_supplier_dashboard(conn, user_id)
    else:
        raise HTTPException(
            status_code=403, detail="Invalid role for dashboard access"
        )


async def _get_superadmin_dashboard(
    conn: asyncpg.Connection,
) -> SuperAdminDashboard:
    """Build SUPERADMIN dashboard with system-wide metrics."""
    try:
        # Fetch all data in parallel for better performance
        revenue = await dashboard_repo.get_total_revenue(conn)
        orders = await dashboard_repo.get_total_orders(conn)
        suppliers = await dashboard_repo.get_active_suppliers_count(conn)
        low_stock = await dashboard_repo.get_low_stock_count(conn)

        revenue_trend_data = await dashboard_repo.get_revenue_trend(conn, months=6)
        order_status_data = await dashboard_repo.get_order_status_breakdown(conn)
        top_suppliers_data = await dashboard_repo.get_top_suppliers(conn, limit=5)

        # Build response
        cards = SuperAdminCards(
            revenue=revenue,
            orders=orders,
            suppliers=suppliers,
            low_stock=low_stock,
        )

        charts = SuperAdminCharts(
            revenue_trend=[
                RevenueTrendItem(month=item["month"], revenue=item["revenue"])
                for item in revenue_trend_data
            ],
            order_status=[
                OrderStatusItem(status=item["status"], count=item["count"])
                for item in order_status_data
            ],
            top_suppliers=[
                TopSupplierItem(supplier=item["supplier"], orders=item["orders"])
                for item in top_suppliers_data
            ],
        )

        return SuperAdminDashboard(cards=cards, charts=charts)

    except asyncpg.PostgresError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while fetching dashboard: {str(exc)}",
        )


async def _get_supplier_dashboard(
    conn: asyncpg.Connection, user_id: str
) -> SupplierDashboard:
    """Build SUPPLIER dashboard with supplier-specific metrics."""
    try:
        # Fetch all data in parallel
        revenue = await dashboard_repo.get_supplier_revenue(conn, user_id)
        orders = await dashboard_repo.get_supplier_orders_count(conn, user_id)
        pending_orders = await dashboard_repo.get_supplier_pending_orders(conn, user_id)
        low_stock = await dashboard_repo.get_supplier_low_stock_count(conn, user_id)

        sales_trend_data = await dashboard_repo.get_supplier_sales_trend(
            conn, user_id, months=6
        )
        order_status_data = await dashboard_repo.get_supplier_order_status(
            conn, user_id
        )
        top_products_data = await dashboard_repo.get_supplier_top_products(
            conn, user_id, limit=5
        )

        # Build response
        cards = SupplierCards(
            revenue=revenue,
            orders=orders,
            pending_orders=pending_orders,
            low_stock=low_stock,
        )

        charts = SupplierCharts(
            sales_trend=[
                SalesTrendItem(month=item["month"], sales=item["sales"])
                for item in sales_trend_data
            ],
            order_status=[
                OrderStatusItem(status=item["status"], count=item["count"])
                for item in order_status_data
            ],
            top_products=[
                TopProductItem(product=item["product"], quantity=item["quantity"])
                for item in top_products_data
            ],
        )

        return SupplierDashboard(cards=cards, charts=charts)

    except asyncpg.PostgresError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while fetching dashboard: {str(exc)}",
        )
