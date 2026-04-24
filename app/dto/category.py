from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class CategoryCreate(BaseModel):
    user_id: str
    category_name: str
    description: Optional[str] = None
    parent_category_id: Optional[str] = None


class CategoryUpdate(BaseModel):
    category_name: Optional[str] = None
    description: Optional[str] = None
    parent_category_id: Optional[str] = None


class CategoryRead(BaseModel):
    category_id: str
    user_id: str
    category_name: str
    description: Optional[str] = None
    parent_category_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None