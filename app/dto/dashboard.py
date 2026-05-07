"""
Dashboard DTOs for SUPERADMIN and SUPPLIER roles.
"""

from pydantic import BaseModel


# ── Chart Data Models ────────────────────────────────────────────────


class RevenueTrendItem(BaseModel):
    month: str
    revenue: float


class OrderStatusItem(BaseModel):
    status: str
    count: int


class TopSupplierItem(BaseModel):
    supplier: str
    orders: int


class SalesTrendItem(BaseModel):
    month: str
    sales: float


class TopProductItem(BaseModel):
    product: str
    quantity: int


# ── Dashboard Cards ──────────────────────────────────────────────────


class SuperAdminCards(BaseModel):
    revenue: float
    orders: int
    suppliers: int
    low_stock: int


class SupplierCards(BaseModel):
    revenue: float
    orders: int
    pending_orders: int
    low_stock: int


# ── Dashboard Charts ─────────────────────────────────────────────────


class SuperAdminCharts(BaseModel):
    revenue_trend: list[RevenueTrendItem]
    order_status: list[OrderStatusItem]
    top_suppliers: list[TopSupplierItem]


class SupplierCharts(BaseModel):
    sales_trend: list[SalesTrendItem]
    order_status: list[OrderStatusItem]
    top_products: list[TopProductItem]


# ── Dashboard Response ───────────────────────────────────────────────


class SuperAdminDashboard(BaseModel):
    role: str = "SUPERADMIN"
    cards: SuperAdminCards
    charts: SuperAdminCharts


class SupplierDashboard(BaseModel):
    role: str = "SUPPLIER"
    cards: SupplierCards
    charts: SupplierCharts
