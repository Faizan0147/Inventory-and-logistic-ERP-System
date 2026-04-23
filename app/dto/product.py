from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class ProductCreate(BaseModel):
    supplier_id: str
    category_id: Optional[str] = None
    product_name: str
    description: Optional[str] = None
    sku: str                                     # NOT NULL UNIQUE in schema
    price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    weight: Optional[Decimal] = None
    status: str = "Active"


class ProductUpdate(BaseModel):
    supplier_id: Optional[str] = None
    category_id: Optional[str] = None
    product_name: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    weight: Optional[Decimal] = None
    status: Optional[str] = None


class ProductRead(BaseModel):
    product_id: str
    supplier_id: str
    user_id: str
    category_id: Optional[str] = None
    product_name: str
    description: Optional[str] = None
    sku: str
    price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    weight: Optional[Decimal] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None