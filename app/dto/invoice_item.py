from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel


# ── Nested summary models ────────────────────────────────────────────

class InvoiceSummary(BaseModel):
    invoice_id: str
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    total_amount: Optional[Decimal] = None
    status: Optional[str] = None


class ProductSummary(BaseModel):
    product_id: str
    product_name: str
    sku: str
    price: Optional[Decimal] = None


# ── Invoice Item DTOs ────────────────────────────────────────────────

class InvoiceItemCreate(BaseModel):
    invoice_id: str
    product_id: str
    quantity: int
    price: Optional[float] = None


class InvoiceItemUpdate(BaseModel):
    quantity: Optional[int] = None
    price: Optional[float] = None


class InvoiceItemRead(BaseModel):
    invoice_item_id: str
    invoice_id: str
    product_id: str
    user_id: str
    quantity: Optional[int] = None
    price: Optional[float] = None
    # Nested
    invoice: Optional[InvoiceSummary] = None
    product: Optional[ProductSummary] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
