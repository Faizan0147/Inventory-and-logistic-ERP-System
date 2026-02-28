from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from app.dto.supplierbankdetails import SupplierBankDetailsRead

# Supplier DTOs

class SupplierCreate(BaseModel):
    name: str
    contact_info: Optional[str] = None
    address: Optional[str] = None


class SupplierUpdate(BaseModel):        
    name: Optional[str] = None
    contact_info: Optional[str] = None
    address: Optional[str] = None


class SupplierRead(BaseModel):
    supplier_id: UUID
    name: str
    contact_info: Optional[str] = None
    address: Optional[str] = None


# ─────────────────────────────────────────────
# Supplier with nested bank details (rich response)
# ─────────────────────────────────────────────

class SupplierWithBankDetails(SupplierRead):
    bank_details: list[SupplierBankDetailsRead] = []
