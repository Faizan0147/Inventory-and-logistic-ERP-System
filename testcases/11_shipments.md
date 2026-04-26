# Shipments API Test Cases
**Base URL:** `/api/v1/shipments`
**Status:** ⏳ Pending
**Prerequisites:** Valid `purchase_order_id`, optional `warehouse_id`

---

## 1. CREATE (POST `/`)

**1.1 Full Valid Shipment**
```json
{
  "purchase_order_id": "<po_id>",
  "warehouse_id": "<warehouse_id>",
  "carrier_name": "DHL",
  "tracking_number": "DHL-2026-001",
  "shipment_date": "2026-04-25",
  "estimated_arrival": "2026-05-02",
  "status": "Pending",
  "notes": "Handle with care"
}
Expected: 201 Created
```

**1.2 Minimum Required Fields**
```json
{
  "purchase_order_id": "<po_id>"
}
Expected: 201 Created
```

**1.3 Duplicate tracking_number**
```json
{
  "purchase_order_id": "<po_id>",
  "tracking_number": "DHL-2026-001"
}
Expected: 409 — {"detail": "A shipment with tracking number 'DHL-2026-001' already exists."}
```

**1.4 Missing purchase_order_id**
```json
{
  "carrier_name": "DHL",
  "tracking_number": "DHL-2026-002"
}
Expected: 422 — {"detail": "purchase_order_id is required"}
```

**1.5 Invalid carrier_name**
```json
{
  "purchase_order_id": "<po_id>",
  "carrier_name": "InvalidCarrier"
}
Expected: 422 (allowed: DHL, FedEx, UPS, Aramex)
```

**1.6 Invalid status value**
```json
{
  "purchase_order_id": "<po_id>",
  "status": "InvalidStatus"
}
Expected: 422 (allowed: Pending, In Transit, Delivered, Returned, Cancelled)
```

**1.7 Invalid purchase_order_id**
```json
{
  "purchase_order_id": "non-existent-po"
}
Expected: 409 — {"detail": "Invalid purchase_order_id or warehouse_id."}
```

---

## 2. LIST (GET `/`)

**2.1 List All**
```
GET /api/v1/shipments
Expected: 200 — Array of shipment objects
```

**2.2 Pagination**
```
GET /api/v1/shipments?offset=0&limit=5
Expected: 200 — Max 5 shipments
```

---

## 3. GET Single (GET `/{shipment_id}`)

**3.1 Valid ID**
```
GET /api/v1/shipments/{shipment_id}
Expected: 200 — Shipment object
```

**3.2 Invalid ID**
```
GET /api/v1/shipments/non-existent-id
Expected: 404 — {"detail": "Shipment not found"}
```

---

## 4. UPDATE (PUT `/{shipment_id}`)

**4.1 Update Status**
```json
{ "status": "In Transit" }
Expected: 200 — Updated shipment object
```

**4.2 Update Arrival Info**
```json
{
  "actual_arrival": "2026-05-01",
  "status": "Delivered"
}
Expected: 200
```

**4.3 Non-existent Shipment**
```
PUT /api/v1/shipments/non-existent-id
Expected: 404 — {"detail": "Shipment not found or access denied"}
```

---

## 5. DELETE (DELETE `/{shipment_id}`)

**5.1 Valid Delete**
```
DELETE /api/v1/shipments/{shipment_id}
Expected: 200 — {"message": "Shipment deleted successfully"}
```

**5.2 Non-existent Shipment**
```
DELETE /api/v1/shipments/non-existent-id
Expected: 404 — {"detail": "Shipment not found or access denied"}
```

**5.3 Soft Delete Verification**
```
1. DELETE /api/v1/shipments/{shipment_id}  → 200
2. GET    /api/v1/shipments/{shipment_id}  → 404
```
