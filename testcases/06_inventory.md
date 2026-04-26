# Inventory API Test Cases
**Base URL:** `/api/v1/inventory`
**Status:** ⏳ Pending
**Prerequisites:** Valid `product_id`, valid `warehouse_id`

---

## 1. CREATE (POST `/`)

**1.1 Full Valid Inventory**
```json
{
  "product_id": "<product_id>",
  "warehouse_id": "<warehouse_id>",
  "quantity": 100,
  "reorder_level": 10,
  "last_restocked": "2026-04-25T00:00:00"
}
Expected: 201 Created
```

**1.2 Minimum Required Fields**
```json
{
  "product_id": "<product_id>",
  "warehouse_id": "<warehouse_id>",
  "quantity": 50
}
Expected: 201 Created
```

**1.3 Duplicate product+warehouse Combination**
```json
{
  "product_id": "<same_product_id>",
  "warehouse_id": "<same_warehouse_id>",
  "quantity": 20
}
Expected: 409 — {"detail": "An inventory record for this product and warehouse already exists."}
```

**1.4 Missing product_id**
```json
{
  "warehouse_id": "<warehouse_id>",
  "quantity": 50
}
Expected: 422 — {"detail": "product_id is required"}
```

**1.5 Missing warehouse_id**
```json
{
  "product_id": "<product_id>",
  "quantity": 50
}
Expected: 422 — {"detail": "warehouse_id is required"}
```

**1.6 Invalid product_id**
```json
{
  "product_id": "non-existent-product",
  "warehouse_id": "<warehouse_id>",
  "quantity": 10
}
Expected: 409 — {"detail": "Invalid product_id or warehouse_id."}
```

**1.7 Negative Quantity**
```json
{
  "product_id": "<product_id>",
  "warehouse_id": "<warehouse_id>",
  "quantity": -5
}
Expected: 409 (DB check constraint)
```

---

## 2. LIST (GET `/`)

**2.1 List All**
```
GET /api/v1/inventory
Expected: 200 — Array of inventory objects
```

**2.2 Pagination**
```
GET /api/v1/inventory?offset=0&limit=5
Expected: 200 — Max 5 records
```

---

## 3. GET Single (GET `/{inventory_id}`)

**3.1 Valid ID**
```
GET /api/v1/inventory/{inventory_id}
Expected: 200 — Inventory object
```

**3.2 Invalid ID**
```
GET /api/v1/inventory/non-existent-id
Expected: 404 — {"detail": "Inventory not found"}
```

---

## 4. UPDATE (PUT `/{inventory_id}`)

**4.1 Update Quantity**
```json
{ "quantity": 200 }
Expected: 200 — Updated inventory object
```

**4.2 Update Reorder Level**
```json
{ "reorder_level": 25 }
Expected: 200
```

**4.3 Non-existent Inventory**
```
PUT /api/v1/inventory/non-existent-id
Expected: 404 — {"detail": "Inventory not found or access denied"}
```

---

## 5. DELETE (DELETE `/{inventory_id}`)

**5.1 Valid Delete**
```
DELETE /api/v1/inventory/{inventory_id}
Expected: 200 — {"message": "Inventory deleted successfully"}
```

**5.2 Non-existent Inventory**
```
DELETE /api/v1/inventory/non-existent-id
Expected: 404 — {"detail": "Inventory not found or access denied"}
```

**5.3 Soft Delete Verification**
```
1. DELETE /api/v1/inventory/{inventory_id}  → 200
2. GET    /api/v1/inventory/{inventory_id}  → 404
```
