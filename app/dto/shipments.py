from typing import Optional, Literal
from datetime import datetime, date
from pydantic import BaseModel

CarrierName = Literal["DHL", "FedEx", "UPS", "Aramex"]
ShipmentStatus = Literal["Pending", "In Transit", "Delivered", "Returned", "Cancelled"]


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
    purchase_order_id: str
    user_id: str
    warehouse_id: Optional[str] = None
    carrier_name: Optional[str] = None
    tracking_number: Optional[str] = None
    shipment_date: Optional[date] = None
    estimated_arrival: Optional[date] = None
    actual_arrival: Optional[date] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
