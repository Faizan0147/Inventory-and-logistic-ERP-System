from typing import Optional, Literal
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel

CarrierName = Literal["DHL", "FedEx", "UPS", "Aramex"]
ShipmentStatus = Literal["Pending", "In Transit", "Delivered", "Returned", "Cancelled"]


# ── Nested summary models ────────────────────────────────────────────


class PurchaseOrderSummary(BaseModel):
    po_id: str
    order_number: Optional[str] = None
    order_date: Optional[date] = None
    status: Optional[str] = None
    supplier_id: Optional[str] = None


class WarehouseSummary(BaseModel):
    warehouse_id: str
    warehouse_name: str
    location: Optional[str] = None
    city: Optional[str] = None


# ── Shipment DTOs ────────────────────────────────────────────────────


class ShipmentCreate(BaseModel):
    purchase_order_id: str
    warehouse_id: Optional[str] = None
    carrier_name: Optional[CarrierName] = None
    tracking_number: Optional[str] = None
    shipment_date: Optional[date] = None
    estimated_arrival: Optional[date] = None
    status: Optional[ShipmentStatus] = None
    notes: Optional[str] = None


class ShipmentUpdate(BaseModel):
    warehouse_id: Optional[str] = None
    carrier_name: Optional[CarrierName] = None
    tracking_number: Optional[str] = None
    shipment_date: Optional[date] = None
    estimated_arrival: Optional[date] = None
    actual_arrival: Optional[date] = None
    status: Optional[ShipmentStatus] = None
    notes: Optional[str] = None


class ShipmentRead(BaseModel):
    shipment_id: str
    po_id: str
    user_id: str
    warehouse_id: Optional[str] = None
    carrier_name: Optional[str] = None
    tracking_number: Optional[str] = None
    shipment_date: Optional[date] = None
    estimated_arrival: Optional[date] = None
    actual_arrival: Optional[date] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    # Nested
    purchase_order: Optional[PurchaseOrderSummary] = None
    warehouse: Optional[WarehouseSummary] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
