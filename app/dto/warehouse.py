from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class WarehouseCreate(BaseModel):
    warehouse_name: str
    location: Optional[str] = None
    city: Optional[str] = None
    capacity: Optional[int] = None
    phone: Optional[str] = None
    manager_id: Optional[str] = None
    is_active: bool = True


class WarehouseUpdate(BaseModel):
    warehouse_name: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    capacity: Optional[int] = None
    phone: Optional[str] = None
    manager_id: Optional[str] = None
    is_active: Optional[bool] = None


class WarehouseRead(BaseModel):
    warehouse_id: str
    warehouse_name: str
    location: Optional[str] = None
    city: Optional[str] = None
    capacity: Optional[int] = None
    phone: Optional[str] = None
    manager_id: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None