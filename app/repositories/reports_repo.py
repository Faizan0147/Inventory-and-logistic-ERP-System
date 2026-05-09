from __future__ import annotations

from typing import Any, Optional

import asyncpg


def _scope_where(alias: str, user_id: Optional[str]) -> tuple[str, list[Any]]:
    if user_id:
        return f" AND {alias}.user_id = $1", [user_id]
    return "", []


async def get_users_summary(conn: asyncpg.Connection, user_id: Optional[str]) -> dict[str, Any]:
    scope, params = _scope_where("u", user_id)
    total_row = await conn.fetchrow(
        f"SELECT COUNT(*) AS count FROM users u WHERE u.deleted = FALSE{scope}",
        *params,
    )
    active_row = await conn.fetchrow(
        f"SELECT COUNT(*) AS count FROM users u WHERE u.deleted = FALSE AND u.is_active = TRUE{scope}",
        *params,
    )
    disabled_row = await conn.fetchrow(
        f"SELECT COUNT(*) AS count FROM users u WHERE u.deleted = FALSE AND u.is_active = FALSE{scope}",
        *params,
    )
    role_rows = await conn.fetch(
        f"""
        SELECT u.role, COUNT(*) AS count
        FROM users u
        WHERE u.deleted = FALSE{scope}
        GROUP BY u.role
        ORDER BY count DESC, u.role
        """,
        *params,
    )
    return {
        "total_users": int(total_row["count"]) if total_row else 0,
        "active_users": int(active_row["count"]) if active_row else 0,
        "disabled_users": int(disabled_row["count"]) if disabled_row else 0,
        "users_by_role": [{"role": r["role"], "count": int(r["count"])} for r in role_rows],
    }


async def get_users_rows(conn: asyncpg.Connection, user_id: Optional[str]) -> list[dict[str, Any]]:
    scope, params = _scope_where("u", user_id)
    rows = await conn.fetch(
        f"""
        SELECT u.user_id, u.name, u.email, u.role,
               CASE WHEN u.is_active THEN 'Active' ELSE 'Disabled' END AS status,
               u.created_at
        FROM users u
        WHERE u.deleted = FALSE{scope}
        ORDER BY u.created_at DESC, u.user_id
        """,
        *params,
    )
    return [dict(r) for r in rows]


async def get_categories_summary(conn: asyncpg.Connection, user_id: Optional[str]) -> dict[str, Any]:
    scope, params = _scope_where("c", user_id)
    total = await conn.fetchrow(
        f"SELECT COUNT(*) AS count FROM categories c WHERE c.deleted = FALSE{scope}", *params
    )
    parents = await conn.fetchrow(
        f"""
        SELECT COUNT(*) AS count
        FROM categories c
        WHERE c.deleted = FALSE AND c.parent_category_id IS NULL{scope}
        """,
        *params,
    )
    children = await conn.fetchrow(
        f"""
        SELECT COUNT(*) AS count
        FROM categories c
        WHERE c.deleted = FALSE AND c.parent_category_id IS NOT NULL{scope}
        """,
        *params,
    )
    ppc = await conn.fetch(
        f"""
        SELECT c.category_name AS name, COUNT(p.product_id) AS count
        FROM categories c
        LEFT JOIN products p ON p.category_id = c.category_id AND p.deleted = FALSE
        WHERE c.deleted = FALSE{scope}
        GROUP BY c.category_id, c.category_name
        ORDER BY count DESC, c.category_name
        """,
        *params,
    )
    return {
        "total_categories": int(total["count"]) if total else 0,
        "parent_categories": int(parents["count"]) if parents else 0,
        "child_categories": int(children["count"]) if children else 0,
        "products_per_category": [{"name": r["name"], "count": int(r["count"])} for r in ppc],
    }


async def get_categories_rows(conn: asyncpg.Connection, user_id: Optional[str]) -> list[dict[str, Any]]:
    scope, params = _scope_where("c", user_id)
    rows = await conn.fetch(
        f"""
        SELECT c.category_id, c.category_name,
               pcat.category_name AS parent_category,
               COUNT(p.product_id) AS product_count,
               c.created_at
        FROM categories c
        LEFT JOIN categories pcat
            ON pcat.category_id = c.parent_category_id AND pcat.deleted = FALSE
        LEFT JOIN products p ON p.category_id = c.category_id AND p.deleted = FALSE
        WHERE c.deleted = FALSE{scope}
        GROUP BY c.category_id, c.category_name, pcat.category_name, c.created_at
        ORDER BY c.created_at DESC, c.category_name
        """,
        *params,
    )
    return [{**dict(r), "product_count": int(r["product_count"])} for r in rows]


async def get_products_summary(conn: asyncpg.Connection, user_id: Optional[str]) -> dict[str, Any]:
    scope, params = _scope_where("p", user_id)
    total = await conn.fetchrow(
        f"SELECT COUNT(*) AS count FROM products p WHERE p.deleted = FALSE{scope}", *params
    )
    active = await conn.fetchrow(
        f"SELECT COUNT(*) AS count FROM products p WHERE p.deleted = FALSE AND p.status = 'Active'{scope}",
        *params,
    )
    inactive = await conn.fetchrow(
        f"SELECT COUNT(*) AS count FROM products p WHERE p.deleted = FALSE AND p.status <> 'Active'{scope}",
        *params,
    )
    by_supplier = await conn.fetch(
        f"""
        SELECT COALESCE(s.supplier_name, 'Unknown') AS name, COUNT(*) AS count
        FROM products p
        LEFT JOIN suppliers s ON s.supplier_id = p.supplier_id AND s.deleted = FALSE
        WHERE p.deleted = FALSE{scope}
        GROUP BY name
        ORDER BY count DESC, name
        """,
        *params,
    )
    by_category = await conn.fetch(
        f"""
        SELECT COALESCE(c.category_name, 'Uncategorized') AS name, COUNT(*) AS count
        FROM products p
        LEFT JOIN categories c ON c.category_id = p.category_id AND c.deleted = FALSE
        WHERE p.deleted = FALSE{scope}
        GROUP BY name
        ORDER BY count DESC, name
        """,
        *params,
    )
    return {
        "total_products": int(total["count"]) if total else 0,
        "active_products": int(active["count"]) if active else 0,
        "inactive_products": int(inactive["count"]) if inactive else 0,
        "products_by_supplier": [{"name": r["name"], "count": int(r["count"])} for r in by_supplier],
        "products_by_category": [{"name": r["name"], "count": int(r["count"])} for r in by_category],
    }


async def get_products_rows(conn: asyncpg.Connection, user_id: Optional[str]) -> list[dict[str, Any]]:
    scope, params = _scope_where("p", user_id)
    rows = await conn.fetch(
        f"""
        SELECT p.product_id, p.product_name, p.sku,
               s.supplier_name AS supplier, c.category_name AS category,
               p.price, p.cost_price, p.status, p.created_at
        FROM products p
        LEFT JOIN suppliers s ON s.supplier_id = p.supplier_id AND s.deleted = FALSE
        LEFT JOIN categories c ON c.category_id = p.category_id AND c.deleted = FALSE
        WHERE p.deleted = FALSE{scope}
        ORDER BY p.created_at DESC, p.product_name
        """,
        *params,
    )
    return [dict(r) for r in rows]


async def get_inventory_summary(conn: asyncpg.Connection, user_id: Optional[str]) -> dict[str, Any]:
    scope, params = _scope_where("i", user_id)
    total_qty = await conn.fetchrow(
        f"SELECT COALESCE(SUM(i.quantity), 0) AS total FROM inventory i WHERE i.deleted = FALSE{scope}",
        *params,
    )
    low_stock = await conn.fetchrow(
        f"""
        SELECT COUNT(*) AS count
        FROM inventory i
        WHERE i.deleted = FALSE AND i.quantity <= i.reorder_level AND i.reorder_level > 0{scope}
        """,
        *params,
    )
    by_wh = await conn.fetch(
        f"""
        SELECT COALESCE(w.warehouse_name, 'Unknown') AS warehouse,
               COALESCE(SUM(i.quantity), 0) AS quantity
        FROM inventory i
        LEFT JOIN warehouses w ON w.warehouse_id = i.warehouse_id AND w.deleted = FALSE
        WHERE i.deleted = FALSE{scope}
        GROUP BY warehouse
        ORDER BY quantity DESC, warehouse
        """,
        *params,
    )
    return {
        "total_inventory_quantity": int(total_qty["total"]) if total_qty else 0,
        "low_stock_products": int(low_stock["count"]) if low_stock else 0,
        "reorder_alerts": int(low_stock["count"]) if low_stock else 0,
        "inventory_by_warehouse": [
            {"warehouse": r["warehouse"], "quantity": int(r["quantity"])} for r in by_wh
        ],
    }


async def get_inventory_rows(conn: asyncpg.Connection, user_id: Optional[str]) -> list[dict[str, Any]]:
    scope, params = _scope_where("i", user_id)
    rows = await conn.fetch(
        f"""
        SELECT p.product_name AS product, w.warehouse_name AS warehouse,
               i.quantity, i.reorder_level, i.last_restocked, i.updated_at
        FROM inventory i
        LEFT JOIN products p ON p.product_id = i.product_id AND p.deleted = FALSE
        LEFT JOIN warehouses w ON w.warehouse_id = i.warehouse_id AND w.deleted = FALSE
        WHERE i.deleted = FALSE{scope}
        ORDER BY i.updated_at DESC, p.product_name
        """,
        *params,
    )
    return [dict(r) for r in rows]


async def get_purchase_orders_summary(conn: asyncpg.Connection, user_id: Optional[str]) -> dict[str, Any]:
    scope, params = _scope_where("po", user_id)
    summary = await conn.fetchrow(
        f"""
        SELECT
            COUNT(*) AS total_purchase_orders,
            COUNT(*) FILTER (WHERE po.status IN ('Pending', 'Draft')) AS pending_orders,
            COUNT(*) FILTER (WHERE po.status IN ('Received', 'Approved')) AS completed_orders,
            COUNT(*) FILTER (WHERE po.status = 'Cancelled') AS cancelled_orders,
            COALESCE(SUM(po.total_amount), 0) AS procurement_cost
        FROM purchase_orders po
        WHERE po.deleted = FALSE{scope}
        """,
        *params,
    )
    return {
        "total_purchase_orders": int(summary["total_purchase_orders"]) if summary else 0,
        "pending_orders": int(summary["pending_orders"]) if summary else 0,
        "completed_orders": int(summary["completed_orders"]) if summary else 0,
        "cancelled_orders": int(summary["cancelled_orders"]) if summary else 0,
        "procurement_cost": float(summary["procurement_cost"]) if summary else 0.0,
    }


async def get_purchase_orders_rows(conn: asyncpg.Connection, user_id: Optional[str]) -> list[dict[str, Any]]:
    scope, params = _scope_where("po", user_id)
    rows = await conn.fetch(
        f"""
        SELECT po.order_number AS po_number, s.supplier_name AS supplier,
               w.warehouse_name AS warehouse, po.order_date, po.expected_delivery,
               po.total_amount, po.status
        FROM purchase_orders po
        LEFT JOIN suppliers s ON s.supplier_id = po.supplier_id AND s.deleted = FALSE
        LEFT JOIN warehouses w ON w.warehouse_id = po.warehouse_id AND w.deleted = FALSE
        WHERE po.deleted = FALSE{scope}
        ORDER BY po.order_date DESC NULLS LAST, po.order_number
        """,
        *params,
    )
    return [dict(r) for r in rows]


async def get_purchase_order_items_summary(
    conn: asyncpg.Connection, user_id: Optional[str]
) -> dict[str, Any]:
    scope, params = _scope_where("pi", user_id)
    most_ordered = await conn.fetch(
        f"""
        SELECT COALESCE(p.product_name, 'Unknown') AS name, COALESCE(SUM(pi.quantity), 0) AS count
        FROM purchase_order_items pi
        LEFT JOIN products p ON p.product_id = pi.product_id AND p.deleted = FALSE
        WHERE pi.deleted = FALSE{scope}
        GROUP BY name
        ORDER BY count DESC, name
        LIMIT 10
        """,
        *params,
    )
    qty = await conn.fetchrow(
        f"""
        SELECT COALESCE(SUM(pi.quantity), 0) AS quantity_ordered
        FROM purchase_order_items pi
        WHERE pi.deleted = FALSE{scope}
        """,
        *params,
    )
    by_supplier = await conn.fetch(
        f"""
        SELECT COALESCE(s.supplier_name, 'Unknown') AS name,
               COALESCE(SUM(pi.quantity * COALESCE(pi.price, 0)), 0) AS count
        FROM purchase_order_items pi
        LEFT JOIN purchase_orders po ON po.po_id = pi.po_id AND po.deleted = FALSE
        LEFT JOIN suppliers s ON s.supplier_id = po.supplier_id AND s.deleted = FALSE
        WHERE pi.deleted = FALSE{scope}
        GROUP BY name
        ORDER BY count DESC, name
        """,
        *params,
    )
    return {
        "most_ordered_products": [{"name": r["name"], "count": int(r["count"])} for r in most_ordered],
        "quantity_ordered": int(qty["quantity_ordered"]) if qty else 0,
        "supplier_procurement_volume": [{"name": r["name"], "count": int(r["count"])} for r in by_supplier],
    }


async def get_purchase_order_items_rows(
    conn: asyncpg.Connection, user_id: Optional[str]
) -> list[dict[str, Any]]:
    scope, params = _scope_where("pi", user_id)
    rows = await conn.fetch(
        f"""
        SELECT pi.po_item_id, po.order_number AS po_number, p.product_name AS product,
               pi.quantity, pi.price, (pi.quantity * COALESCE(pi.price, 0)) AS total
        FROM purchase_order_items pi
        LEFT JOIN purchase_orders po ON po.po_id = pi.po_id AND po.deleted = FALSE
        LEFT JOIN products p ON p.product_id = pi.product_id AND p.deleted = FALSE
        WHERE pi.deleted = FALSE{scope}
        ORDER BY pi.created_at DESC, pi.po_item_id
        """,
        *params,
    )
    return [{**dict(r), "total": float(r["total"])} for r in rows]


async def get_invoices_summary(conn: asyncpg.Connection, user_id: Optional[str]) -> dict[str, Any]:
    scope, params = _scope_where("i", user_id)
    summary = await conn.fetchrow(
        f"""
        SELECT
            COALESCE(SUM(i.total_amount), 0) FILTER (WHERE i.status = 'Paid') AS total_revenue,
            COUNT(*) FILTER (WHERE i.status = 'Paid') AS paid_invoices,
            COUNT(*) FILTER (WHERE i.status = 'Pending') AS pending_invoices,
            COUNT(*) FILTER (WHERE i.status = 'Cancelled') AS cancelled_invoices
        FROM invoices i
        WHERE i.deleted = FALSE{scope}
        """,
        *params,
    )
    return {
        "total_revenue": float(summary["total_revenue"]) if summary else 0.0,
        "paid_invoices": int(summary["paid_invoices"]) if summary else 0,
        "pending_invoices": int(summary["pending_invoices"]) if summary else 0,
        "cancelled_invoices": int(summary["cancelled_invoices"]) if summary else 0,
    }


async def get_invoices_rows(conn: asyncpg.Connection, user_id: Optional[str]) -> list[dict[str, Any]]:
    scope, params = _scope_where("i", user_id)
    rows = await conn.fetch(
        f"""
        SELECT i.invoice_number, s.supplier_name AS supplier, po.order_number AS po_number,
               i.invoice_date, i.total_amount, i.status
        FROM invoices i
        LEFT JOIN suppliers s ON s.supplier_id = i.supplier_id AND s.deleted = FALSE
        LEFT JOIN purchase_orders po ON po.po_id = i.po_id AND po.deleted = FALSE
        WHERE i.deleted = FALSE{scope}
        ORDER BY i.invoice_date DESC NULLS LAST, i.invoice_number
        """,
        *params,
    )
    return [dict(r) for r in rows]


async def get_invoice_items_summary(
    conn: asyncpg.Connection, user_id: Optional[str]
) -> dict[str, Any]:
    scope, params = _scope_where("ii", user_id)
    best = await conn.fetch(
        f"""
        SELECT COALESCE(p.product_name, 'Unknown') AS name, COALESCE(SUM(ii.quantity), 0) AS count
        FROM invoice_items ii
        LEFT JOIN products p ON p.product_id = ii.product_id AND p.deleted = FALSE
        WHERE ii.deleted = FALSE{scope}
        GROUP BY name
        ORDER BY count DESC, name
        LIMIT 10
        """,
        *params,
    )
    revenue = await conn.fetch(
        f"""
        SELECT COALESCE(p.product_name, 'Unknown') AS name,
               COALESCE(SUM(ii.quantity * COALESCE(ii.price, 0)), 0) AS count
        FROM invoice_items ii
        LEFT JOIN products p ON p.product_id = ii.product_id AND p.deleted = FALSE
        WHERE ii.deleted = FALSE{scope}
        GROUP BY name
        ORDER BY count DESC, name
        LIMIT 10
        """,
        *params,
    )
    qty = await conn.fetchrow(
        f"""
        SELECT COALESCE(SUM(ii.quantity), 0) AS quantity_sold
        FROM invoice_items ii
        WHERE ii.deleted = FALSE{scope}
        """,
        *params,
    )
    return {
        "best_selling_products": [{"name": r["name"], "count": int(r["count"])} for r in best],
        "product_revenue": [{"name": r["name"], "count": int(r["count"])} for r in revenue],
        "quantity_sold": int(qty["quantity_sold"]) if qty else 0,
    }


async def get_invoice_items_rows(conn: asyncpg.Connection, user_id: Optional[str]) -> list[dict[str, Any]]:
    scope, params = _scope_where("ii", user_id)
    rows = await conn.fetch(
        f"""
        SELECT ii.invoice_item_id, i.invoice_number, p.product_name AS product,
               ii.quantity, ii.price, (COALESCE(ii.quantity, 0) * COALESCE(ii.price, 0)) AS total
        FROM invoice_items ii
        LEFT JOIN invoices i ON i.invoice_id = ii.invoice_id AND i.deleted = FALSE
        LEFT JOIN products p ON p.product_id = ii.product_id AND p.deleted = FALSE
        WHERE ii.deleted = FALSE{scope}
        ORDER BY ii.created_at DESC, ii.invoice_item_id
        """,
        *params,
    )
    return [{**dict(r), "total": float(r["total"])} for r in rows]


async def get_shipments_summary(conn: asyncpg.Connection, user_id: Optional[str]) -> dict[str, Any]:
    scope, params = _scope_where("s", user_id)
    summary = await conn.fetchrow(
        f"""
        SELECT
            COUNT(*) FILTER (WHERE s.status IN ('Pending', 'In Transit')) AS active_shipments,
            COUNT(*) FILTER (WHERE s.status = 'Delivered') AS delivered_shipments,
            COUNT(*) FILTER (
                WHERE s.status IN ('Pending', 'In Transit')
                  AND s.estimated_arrival IS NOT NULL
                  AND s.estimated_arrival < CURRENT_DATE
            ) AS delayed_shipments
        FROM shipments s
        WHERE s.deleted = FALSE{scope}
        """,
        *params,
    )
    carriers = await conn.fetch(
        f"""
        SELECT COALESCE(s.carrier_name, 'Unknown') AS carrier,
               COUNT(*) FILTER (WHERE s.status = 'Delivered') AS delivered,
               COUNT(*) AS total
        FROM shipments s
        WHERE s.deleted = FALSE{scope}
        GROUP BY carrier
        ORDER BY delivered DESC, total DESC, carrier
        """,
        *params,
    )
    return {
        "active_shipments": int(summary["active_shipments"]) if summary else 0,
        "delivered_shipments": int(summary["delivered_shipments"]) if summary else 0,
        "delayed_shipments": int(summary["delayed_shipments"]) if summary else 0,
        "carrier_performance": [
            {"carrier": r["carrier"], "delivered": int(r["delivered"]), "total": int(r["total"])}
            for r in carriers
        ],
    }


async def get_shipments_rows(conn: asyncpg.Connection, user_id: Optional[str]) -> list[dict[str, Any]]:
    scope, params = _scope_where("s", user_id)
    rows = await conn.fetch(
        f"""
        SELECT s.shipment_id, s.tracking_number, s.carrier_name AS carrier,
               s.shipment_date, s.estimated_arrival, s.status
        FROM shipments s
        WHERE s.deleted = FALSE{scope}
        ORDER BY s.shipment_date DESC NULLS LAST, s.shipment_id
        """,
        *params,
    )
    return [dict(r) for r in rows]
