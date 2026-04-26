# Purchase Orders API Test Cases
**Base URL:** `/api/v1/purchase-order`
**Status:** ⏳ Pending
**Prerequisites:** Valid `supplier_id`, optional `warehouse_id`

---

## 1. CREATE (POST `/`)

**1.1 Full Valid Purchase Order**
```json
{
  "supplier_id": "<supplier_id>",
  "warehouse_id": "<warehouse_id>",
  "order_number": "PO-2026-001",
  "order_date": "2026-04-25",
  "expected_delivery": "2026-05-10",
  "total_amount": 5000.00,
  "status": "Draft"
}
Expected: 201 Created
```

**1.2 Minimum Required Fields**
```json
{
  "supplier_id": "<supplier_id>"
}
Expected: 201 Created
```

**1.3 Duplicate order_number**
```json
{
  "supplier_id": "<supplier_id>",
  "order_number": "PO-2026-001"
}
Expected: 409 — {"detail": "A purchase order with number 'PO-2026-001' already exists."}
```

**1.4 Missing supplier_id**
```json
{
  "order_number": "PO-2026-002",
  "status": "Draft"
}
Expected: 422 — {"detail": "supplier_id is required"}
```

**1.5 Invalid status value**
```json
{
  "supplier_id": "<supplier_id>",
  "status": "InvalidStatus"
}
Expected: 409 (DB check constraint — allowed: Draft, Pending, Approved, Shipped, Received, Cancelled)
```

**1.6 Invalid supplier_id**
```json
{
  "supplier_id": "non-existent-supplier"
}
Expected: 409 — {"detail": "Invalid supplier_id or warehouse_id."}
```

---

## 2. LIST (GET `/`)

**2.1 List All**
```
GET /api/v1/purchase-order
Expected: 200 — Array of purchase order objects
```

**2.2 Pagination**
```
GET /api/v1/purchase-order?offset=0&limit=5
Expected: 200 — Max 5 orders
```

---

## 3. GET Single (GET `/{po_id}`)

**3.1 Valid ID**
```
GET /api/v1/purchase-order/{po_id}
Expected: 200 — Purchase order object
```

**3.2 Invalid ID**
```
GET /api/v1/purchase-order/non-existent-id
Expected: 404 — {"detail": "Purchase order not found"}
```

---

## 4. UPDATE (PUT `/{po_id}`)

**4.1 Update Status**
```json
{ "status": "Approved" }
Expected: 200 — Updated purchase order object
```

**4.2 Update Multiple Fields**
```json
{
  "expected_delivery": "2026-05-15",
  "total_amount": 6500.00,
  "status": "Pending"
}
Expected: 200
```

**4.3 Non-existent PO**
```
PUT /api/v1/purchase-order/non-existent-id
Expected: 404 — {"detail": "Purchase order not found or access denied"}
```

---

## 5. DELETE (DELETE `/{po_id}`)

**5.1 Valid Delete**
```
DELETE /api/v1/purchase-order/{po_id}
Expected: 200 — {"message": "Purchase order deleted successfully"}
```

**5.2 Non-existent PO**
```
DELETE /api/v1/purchase-order/non-existent-id
Expected: 404 — {"detail": "Purchase order not found or access denied"}
```

**5.3 Soft Delete Verification**
```
1. DELETE /api/v1/purchase-order/{po_id}  → 200
2. GET    /api/v1/purchase-order/{po_id}  → 404
```
