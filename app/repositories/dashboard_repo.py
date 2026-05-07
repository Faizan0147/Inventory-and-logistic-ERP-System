"""
Dashboard repository: database queries for SUPERADMIN and SUPPLIER dashboards.
"""

import asyncpg
from datetime import datetime, timedelta


# ══════════════════════════════════════════════════════════════════════
# SUPERADMIN QUERIES
# ══════════════════════════════════════════════════════════════════════


async def get_total_revenue(conn: asyncpg.Connection) -> float:
    """Get total revenue from all paid invoices."""
    query = """
        SELECT COALESCE(SUM(total_amount), 0) as revenue
        FROM invoices
        WHERE deleted = FALSE AND status = 'Paid'
    """
    row = await conn.fetchrow(query)
    return float(row["revenue"]) if row else 0.0


async def get_total_orders(conn: asyncpg.Connection) -> int:
    """Get total count of purchase orders."""
    query = """
        SELECT COUNT(*) as count
        FROM purchase_orders
        WHERE deleted = FALSE
    """
    row = await conn.fetchrow(query)
    return int(row["count"]) if row else 0


async def get_active_suppliers_count(conn: asyncpg.Connection) -> int:
    """Get count of active suppliers."""
    query = """
        SELECT COUNT(*) as count
        FROM suppliers
        WHERE deleted = FALSE AND status = 'Active'
    """
    row = await conn.fetchrow(query)
    return int(row["count"]) if row else 0


async def get_low_stock_count(conn: asyncpg.Connection) -> int:
    """Get count of inventory items below reorder level."""
    query = """
        SELECT COUNT(*) as count
        FROM inventory
        WHERE deleted = FALSE 
          AND quantity <= reorder_level
          AND reorder_level > 0
    """
    row = await conn.fetchrow(query)
    return int(row["count"]) if row else 0


async def get_revenue_trend(conn: asyncpg.Connection, months: int = 6) -> list[dict]:
    """Get monthly revenue trend for the last N months."""
    query = """
        WITH month_series AS (
            SELECT 
                TO_CHAR(DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month' * generate_series), 'Mon') as month,
                DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month' * generate_series) as month_date
            FROM generate_series(0, $1 - 1)
            ORDER BY month_date
        )
        SELECT 
            ms.month,
            COALESCE(SUM(i.total_amount), 0) as revenue
        FROM month_series ms
        LEFT JOIN invoices i ON 
            DATE_TRUNC('month', i.invoice_date) = ms.month_date
            AND i.deleted = FALSE
            AND i.status = 'Paid'
        GROUP BY ms.month, ms.month_date
        ORDER BY ms.month_date
    """
    rows = await conn.fetch(query, months)
    return [{"month": row["month"], "revenue": float(row["revenue"])} for row in rows]


async def get_order_status_breakdown(conn: asyncpg.Connection) -> list[dict]:
    """Get purchase order count by status."""
    query = """
        SELECT 
            status,
            COUNT(*) as count
        FROM purchase_orders
        WHERE deleted = FALSE
        GROUP BY status
        ORDER BY count DESC
    """
    rows = await conn.fetch(query)
    return [{"status": row["status"], "count": int(row["count"])} for row in rows]


async def get_top_suppliers(conn: asyncpg.Connection, limit: int = 5) -> list[dict]:
    """Get top suppliers by order count."""
    query = """
        SELECT 
            s.supplier_name as supplier,
            COUNT(po.po_id) as orders
        FROM suppliers s
        LEFT JOIN purchase_orders po ON s.supplier_id = po.supplier_id 
            AND po.deleted = FALSE
        WHERE s.deleted = FALSE
        GROUP BY s.supplier_id, s.supplier_name
        ORDER BY orders DESC
        LIMIT $1
    """
    rows = await conn.fetch(query, limit)
    return [{"supplier": row["supplier"], "orders": int(row["orders"])} for row in rows]


# ══════════════════════════════════════════════════════════════════════
# SUPPLIER QUERIES
# ══════════════════════════════════════════════════════════════════════


async def get_supplier_revenue(conn: asyncpg.Connection, user_id: str) -> float:
    """Get total revenue for a specific supplier."""
    query = """
        SELECT COALESCE(SUM(i.total_amount), 0) as revenue
        FROM invoices i
        JOIN suppliers s ON i.supplier_id = s.supplier_id
        WHERE i.deleted = FALSE 
          AND i.status = 'Paid'
          AND s.user_id = $1
          AND s.deleted = FALSE
    """
    row = await conn.fetchrow(query, user_id)
    return float(row["revenue"]) if row else 0.0


async def get_supplier_orders_count(conn: asyncpg.Connection, user_id: str) -> int:
    """Get total order count for a specific supplier."""
    query = """
        SELECT COUNT(*) as count
        FROM purchase_orders po
        JOIN suppliers s ON po.supplier_id = s.supplier_id
        WHERE po.deleted = FALSE
          AND s.user_id = $1
          AND s.deleted = FALSE
    """
    row = await conn.fetchrow(query, user_id)
    return int(row["count"]) if row else 0


async def get_supplier_pending_orders(conn: asyncpg.Connection, user_id: str) -> int:
    """Get pending order count for a specific supplier."""
    query = """
        SELECT COUNT(*) as count
        FROM purchase_orders po
        JOIN suppliers s ON po.supplier_id = s.supplier_id
        WHERE po.deleted = FALSE
          AND po.status IN ('Pending', 'Draft')
          AND s.user_id = $1
          AND s.deleted = FALSE
    """
    row = await conn.fetchrow(query, user_id)
    return int(row["count"]) if row else 0


async def get_supplier_low_stock_count(conn: asyncpg.Connection, user_id: str) -> int:
    """Get low stock count for a specific supplier's products."""
    query = """
        SELECT COUNT(*) as count
        FROM inventory inv
        JOIN products p ON inv.product_id = p.product_id
        JOIN suppliers s ON p.supplier_id = s.supplier_id
        WHERE inv.deleted = FALSE
          AND inv.quantity <= inv.reorder_level
          AND inv.reorder_level > 0
          AND s.user_id = $1
          AND s.deleted = FALSE
          AND p.deleted = FALSE
    """
    row = await conn.fetchrow(query, user_id)
    return int(row["count"]) if row else 0


async def get_supplier_sales_trend(
    conn: asyncpg.Connection, user_id: str, months: int = 6
) -> list[dict]:
    """Get monthly sales trend for a specific supplier."""
    query = """
        WITH month_series AS (
            SELECT 
                TO_CHAR(DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month' * generate_series), 'Mon') as month,
                DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month' * generate_series) as month_date
            FROM generate_series(0, $2 - 1)
            ORDER BY month_date
        )
        SELECT 
            ms.month,
            COALESCE(SUM(i.total_amount), 0) as sales
        FROM month_series ms
        LEFT JOIN invoices i ON 
            DATE_TRUNC('month', i.invoice_date) = ms.month_date
            AND i.deleted = FALSE
            AND i.status = 'Paid'
        LEFT JOIN suppliers s ON i.supplier_id = s.supplier_id
            AND s.user_id = $1
            AND s.deleted = FALSE
        GROUP BY ms.month, ms.month_date
        ORDER BY ms.month_date
    """
    rows = await conn.fetch(query, user_id, months)
    return [{"month": row["month"], "sales": float(row["sales"])} for row in rows]


async def get_supplier_order_status(
    conn: asyncpg.Connection, user_id: str
) -> list[dict]:
    """Get order status breakdown for a specific supplier."""
    query = """
        SELECT 
            po.status,
            COUNT(*) as count
        FROM purchase_orders po
        JOIN suppliers s ON po.supplier_id = s.supplier_id
        WHERE po.deleted = FALSE
          AND s.user_id = $1
          AND s.deleted = FALSE
        GROUP BY po.status
        ORDER BY count DESC
    """
    rows = await conn.fetch(query, user_id)
    return [{"status": row["status"], "count": int(row["count"])} for row in rows]


async def get_supplier_top_products(
    conn: asyncpg.Connection, user_id: str, limit: int = 5
) -> list[dict]:
    """Get top products by quantity sold for a specific supplier."""
    query = """
        SELECT 
            p.product_name as product,
            COALESCE(SUM(poi.received_quantity), 0) as quantity
        FROM products p
        JOIN suppliers s ON p.supplier_id = s.supplier_id
        LEFT JOIN purchase_order_items poi ON p.product_id = poi.product_id
            AND poi.deleted = FALSE
        WHERE p.deleted = FALSE
          AND s.user_id = $1
          AND s.deleted = FALSE
        GROUP BY p.product_id, p.product_name
        ORDER BY quantity DESC
        LIMIT $2
    """
    rows = await conn.fetch(query, user_id, limit)
    return [
        {"product": row["product"], "quantity": int(row["quantity"])} for row in rows
    ]
