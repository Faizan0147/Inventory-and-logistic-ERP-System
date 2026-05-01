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


class PurchaseOrderSummary(BaseModel):
    po_id: str
    order_number: Optional[str] = None
    order_date: Optional[date] = None
    status: Optional[str] = None


# ── Invoice DTOs ─────────────────────────────────────────────────────

class InvoiceCreate(BaseModel):
    supplier_id: str
    po_id: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    total_amount: Optional[Decimal] = None
    status: Optional[str] = None


class InvoiceUpdate(BaseModel):
    supplier_id: Optional[str] = None
    po_id: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    total_amount: Optional[Decimal] = None
    status: Optional[str] = None


class InvoiceRead(BaseModel):
    invoice_id: str
    supplier_id: str
    user_id: str
    po_id: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    total_amount: Optional[Decimal] = None
    status: Optional[str] = None
    # Nested
    supplier: Optional[SupplierSummary] = None
    purchase_order: Optional[PurchaseOrderSummary] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
