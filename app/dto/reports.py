from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class RoleCount(BaseModel):
    role: str
    count: int


class NameCount(BaseModel):
    name: str
    count: int


class UsersReportSummary(BaseModel):
    total_users: int
    active_users: int
    disabled_users: int
    users_by_role: list[RoleCount]


class UsersReportRow(BaseModel):
    user_id: str
    name: str
    email: str
    role: str
    status: str
    created_at: Optional[datetime] = None


class UsersReportResponse(BaseModel):
    summary: UsersReportSummary
    rows: list[UsersReportRow]


class CategoriesReportSummary(BaseModel):
    total_categories: int
    parent_categories: int
    child_categories: int
    products_per_category: list[NameCount]


class CategoriesReportRow(BaseModel):
    category_id: str
    category_name: str
    parent_category: Optional[str] = None
    product_count: int
    created_at: Optional[datetime] = None


class CategoriesReportResponse(BaseModel):
    summary: CategoriesReportSummary
    rows: list[CategoriesReportRow]


class ProductsReportSummary(BaseModel):
    total_products: int
    active_products: int
    inactive_products: int
    products_by_supplier: list[NameCount]
    products_by_category: list[NameCount]


class ProductsReportRow(BaseModel):
    product_id: str
    product_name: str
    sku: str
    supplier: Optional[str] = None
    category: Optional[str] = None
    price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    status: str
    created_at: Optional[datetime] = None


class ProductsReportResponse(BaseModel):
    summary: ProductsReportSummary
    rows: list[ProductsReportRow]


class WarehouseQuantity(BaseModel):
    warehouse: str
    quantity: int


class InventoryReportSummary(BaseModel):
    total_inventory_quantity: int
    low_stock_products: int
    reorder_alerts: int
    inventory_by_warehouse: list[WarehouseQuantity]


class InventoryReportRow(BaseModel):
    product: Optional[str] = None
    warehouse: Optional[str] = None
    quantity: int
    reorder_level: Optional[int] = None
    last_restocked: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class InventoryReportResponse(BaseModel):
    summary: InventoryReportSummary
    rows: list[InventoryReportRow]


class PurchaseOrdersReportSummary(BaseModel):
    total_purchase_orders: int
    pending_orders: int
    completed_orders: int
    cancelled_orders: int
    procurement_cost: float


class PurchaseOrdersReportRow(BaseModel):
    po_number: Optional[str] = None
    supplier: Optional[str] = None
    warehouse: Optional[str] = None
    order_date: Optional[date] = None
    expected_delivery: Optional[date] = None
    total_amount: Optional[Decimal] = None
    status: Optional[str] = None


class PurchaseOrdersReportResponse(BaseModel):
    summary: PurchaseOrdersReportSummary
    rows: list[PurchaseOrdersReportRow]


class PurchaseOrderItemsReportSummary(BaseModel):
    most_ordered_products: list[NameCount]
    quantity_ordered: int
    supplier_procurement_volume: list[NameCount]


class PurchaseOrderItemsReportRow(BaseModel):
    po_item_id: str
    po_number: Optional[str] = None
    product: Optional[str] = None
    quantity: int
    price: Optional[Decimal] = None
    total: float


class PurchaseOrderItemsReportResponse(BaseModel):
    summary: PurchaseOrderItemsReportSummary
    rows: list[PurchaseOrderItemsReportRow]


class InvoicesReportSummary(BaseModel):
    total_revenue: float
    paid_invoices: int
    pending_invoices: int
    cancelled_invoices: int


class InvoicesReportRow(BaseModel):
    invoice_number: Optional[str] = None
    supplier: Optional[str] = None
    po_number: Optional[str] = None
    invoice_date: Optional[date] = None
    total_amount: Optional[Decimal] = None
    status: Optional[str] = None


class InvoicesReportResponse(BaseModel):
    summary: InvoicesReportSummary
    rows: list[InvoicesReportRow]


class InvoiceItemsReportSummary(BaseModel):
    best_selling_products: list[NameCount]
    product_revenue: list[NameCount]
    quantity_sold: int


class InvoiceItemsReportRow(BaseModel):
    invoice_item_id: str
    invoice_number: Optional[str] = None
    product: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[Decimal] = None
    total: float


class InvoiceItemsReportResponse(BaseModel):
    summary: InvoiceItemsReportSummary
    rows: list[InvoiceItemsReportRow]


class CarrierPerformance(BaseModel):
    carrier: str
    delivered: int
    total: int


class ShipmentsReportSummary(BaseModel):
    active_shipments: int
    delivered_shipments: int
    delayed_shipments: int
    carrier_performance: list[CarrierPerformance]


class ShipmentsReportRow(BaseModel):
    shipment_id: str
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    shipment_date: Optional[date] = None
    estimated_arrival: Optional[date] = None
    status: Optional[str] = None


class ShipmentsReportResponse(BaseModel):
    summary: ShipmentsReportSummary
    rows: list[ShipmentsReportRow]
