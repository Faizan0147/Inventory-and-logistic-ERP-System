from typing import Optional
from datetime import datetime
from pydantic import BaseModel


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
    product_id: str
    warehouse_id: str
    quantity: int
    reorder_level: Optional[int] = None
    last_restocked: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None