from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field


# ── Nested summary models ────────────────────────────────────────────

class PurchaseOrderSummary(BaseModel):
    po_id: str
    order_number: Optional[str] = None
    order_date: Optional[date] = None
    status: Optional[str] = None


class ProductSummary(BaseModel):
    product_id: str
    product_name: str
    sku: str
    price: Optional[Decimal] = None


# ── PO Item DTOs ─────────────────────────────────────────────────────

class POItemCreate(BaseModel):
    po_id: str
    product_id: str
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")
    price: Optional[Decimal] = None


class POItemUpdate(BaseModel):
    po_id: Optional[str] = None
    product_id: Optional[str] = None
    quantity: Optional[int] = Field(None, gt=0, description="Quantity must be greater than 0")
    price: Optional[Decimal] = None


class POItemRead(BaseModel):
    po_item_id: str
    po_id: str
    product_id: str
    user_id: str
    quantity: int
    price: Optional[Decimal] = None
    # Nested
    purchase_order: Optional[PurchaseOrderSummary] = None
    product: Optional[ProductSummary] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
