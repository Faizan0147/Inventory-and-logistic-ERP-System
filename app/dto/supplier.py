from typing import Optional
from datetime import datetime
from pydantic import BaseModel


# Supplier DTOs

class SupplierCreate(BaseModel):
    supplier_name: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    status: str = "Active"


class SupplierUpdate(BaseModel):
    supplier_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None


class SupplierRead(BaseModel):
    supplier_id: str
    supplier_name: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None