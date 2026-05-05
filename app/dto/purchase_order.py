from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel

# ── Nested summary models ────────────────────────────────────────────


class SupplierSummary(BaseModel):
    supplier_id: str
    supplier_name: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class WarehouseSummary(BaseModel):
    warehouse_id: str
    warehouse_name: str
    location: Optional[str] = None
    city: Optional[str] = None


# ── Purchase Order DTOs ──────────────────────────────────────────────


class PurchaseOrderCreate(BaseModel):
    supplier_id: str
    warehouse_id: Optional[str] = None
    order_number: Optional[str] = None
    order_date: Optional[date] = None
    expected_delivery: Optional[date] = None
    total_amount: Optional[Decimal] = None
    status: Optional[str] = None


class PurchaseOrderUpdate(BaseModel):
    supplier_id: Optional[str] = None
    warehouse_id: Optional[str] = None
    order_number: Optional[str] = None
    order_date: Optional[date] = None
    expected_delivery: Optional[date] = None
    total_amount: Optional[Decimal] = None
    status: Optional[str] = None


class PurchaseOrderRead(BaseModel):
    po_id: str
    supplier_id: str
    user_id: str
    warehouse_id: Optional[str] = None
    order_number: Optional[str] = None
    order_date: Optional[date] = None
    expected_delivery: Optional[date] = None
    total_amount: Optional[Decimal] = None
    status: Optional[str] = None
    # Nested
    supplier: Optional[SupplierSummary] = None
    warehouse: Optional[WarehouseSummary] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
