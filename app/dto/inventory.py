from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel

# ── Nested summary models ────────────────────────────────────────────


class ProductSummary(BaseModel):
    product_id: str
    product_name: str
    sku: str
    price: Optional[Decimal] = None


class WarehouseSummary(BaseModel):
    warehouse_id: str
    warehouse_name: str
    location: Optional[str] = None
    city: Optional[str] = None


# ── Inventory DTOs ───────────────────────────────────────────────────


class InventoryCreate(BaseModel):
    product_id: str
    warehouse_id: str
    quantity: int = 0
    reorder_level: Optional[int] = 0
    last_restocked: Optional[datetime] = None


class InventoryUpdate(BaseModel):
    product_id: Optional[str] = None
    warehouse_id: Optional[str] = None
    quantity: Optional[int] = None
    reorder_level: Optional[int] = None
    last_restocked: Optional[datetime] = None


class InventoryRead(BaseModel):
    inventory_id: str
    user_id: str
    product_id: str
    warehouse_id: str
    quantity: int
    reorder_level: Optional[int] = None
    last_restocked: Optional[datetime] = None
    # Nested
    product: Optional[ProductSummary] = None
    warehouse: Optional[WarehouseSummary] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
