from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel


class ShipmentCreate(BaseModel):
    po_id: str
    warehouse_id: Optional[str] = None
    carrier_name: Optional[str] = None
    tracking_number: Optional[str] = None
    shipment_date: Optional[date] = None
    estimated_arrival: Optional[date] = None
    status: Optional[str] = None


class ShipmentUpdate(BaseModel):
    warehouse_id: Optional[str] = None
    carrier_name: Optional[str] = None
    tracking_number: Optional[str] = None
    shipment_date: Optional[date] = None
    estimated_arrival: Optional[date] = None
    actual_arrival: Optional[date] = None
    status: Optional[str] = None


class ShipmentRead(BaseModel):
    shipment_id: str
    po_id: str
    warehouse_id: Optional[str] = None
    carrier_name: Optional[str] = None
    tracking_number: Optional[str] = None
    shipment_date: Optional[date] = None
    estimated_arrival: Optional[date] = None
    actual_arrival: Optional[date] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None