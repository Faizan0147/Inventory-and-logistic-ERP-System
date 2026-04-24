from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class POItemCreate(BaseModel):
    po_id: str
    product_id: str
    quantity: int
    price: Optional[Decimal] = None


class POItemUpdate(BaseModel):
    po_id: Optional[str] = None
    product_id: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[Decimal] = None


class POItemRead(BaseModel):
    po_item_id: str
    po_id: str
    product_id: str
    user_id: str
    quantity: int
    price: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
