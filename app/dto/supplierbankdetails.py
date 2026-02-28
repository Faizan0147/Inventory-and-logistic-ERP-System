from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class SupplierBankDetailsCreate(BaseModel):
    bank_name: str
    account_number: str
    routing_number: Optional[str] = None

class SupplierBankDetailsRead(BaseModel):
    bank_detail_id: UUID
    supplier_id: UUID
    bank_name: str
    account_number: str
    routing_number: Optional[str] = None
