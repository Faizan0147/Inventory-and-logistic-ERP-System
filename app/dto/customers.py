from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel

CustomerType = Literal["Individual", "Business"]


class CustomerCreate(BaseModel):
    customer_name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    customer_type: CustomerType = "Business"


class CustomerUpdate(BaseModel):
    customer_name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    customer_type: Optional[CustomerType] = None


class CustomerRead(BaseModel):
    customer_id: str
    user_id: str
    customer_name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    customer_type: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
