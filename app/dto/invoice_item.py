from typing import Optional
from datetime import datetime
from pydantic import BaseModel


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
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None