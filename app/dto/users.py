from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    phone_number: Optional[str] = None
    role: str = "SUPPLIER"
    supplier_id: Optional[str] = None

    
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[str] = None
    supplier_id: Optional[str] = None
    is_active: Optional[bool] = None

    

class UserRead(BaseModel):
    user_id: str
    name: str
    email: str
    phone_number: Optional[str] = None
    role: str
    supplier_id: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
