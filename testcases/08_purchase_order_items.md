# Purchase Order Items (POI) API Test Cases
**Base URL:** `/api/v1/poi/{po_id}/items`
**Status:** ⏳ Pending
**Prerequisites:** Valid `po_id`, valid `product_id`

---

## 1. CREATE (POST `/{po_id}/items`)

**1.1 Full Valid PO Item**
```json
POST /api/v1/poi/{po_id}/items
Body:
{
  "po_id": "<po_id>",
  "product_id": "<product_id>",
  "quantity": 10,
  "price": 150.00
}
Expected: 201 Created
```

**1.2 Without Price**
```json
{
  "po_id": "<po_id>",
  "product_id": "<product_id>",
  "quantity": 5
}
Expected: 201 Created
```

**1.3 Missing product_id**
```json
{
  "po_id": "<po_id>",
  "quantity": 5
}
Expected: 422 — {"detail": "product_id is required"}
```

**1.4 Missing quantity**
```json
{
  "po_id": "<po_id>",
  "product_id": "<product_id>"
}
Expected: 422 — {"detail": "quantity is required"}
```

**1.5 Zero or Negative Quantity**
```json
{
  "po_id": "<po_id>",
  "product_id": "<product_id>",
  "quantity": 0
}
Expected: 409 (DB check constraint — quantity must be > 0)
```

**1.6 Invalid po_id**
```json
{
  "po_id": "non-existent-po",
  "product_id": "<product_id>",
  "quantity": 5
}
Expected: 409 — {"detail": "Invalid po_id or product_id."}
```

---

## 2. LIST (GET `/{po_id}/items`)

**2.1 List Items for a PO**
```
GET /api/v1/poi/{po_id}/items
Expected: 200 — Array of PO item objects
```

**2.2 Empty PO**
```
GET /api/v1/poi/{po_id_with_no_items}/items
Expected: 200 — []
```

---

## 3. GET Single (GET `/{po_id}/items/{po_item_id}`)

**3.1 Valid ID**
```
GET /api/v1/poi/{po_id}/items/{po_item_id}
Expected: 200 — PO item object
```

**3.2 Invalid ID**
```
GET /api/v1/poi/{po_id}/items/non-existent-id
Expected: 404 — {"detail": "PO item not found"}
```

---

## 4. UPDATE (PUT `/{po_id}/items/{po_item_id}`)

**4.1 Update Quantity and Price**
```json
{
  "quantity": 20,
  "price": 140.00
}
Expected: 200 — Updated PO item object
```

**4.2 Non-existent Item**
```
PUT /api/v1/poi/{po_id}/items/non-existent-id
Expected: 404 — {"detail": "PO item not found or access denied"}
```

---

## 5. DELETE (DELETE `/{po_id}/items/{po_item_id}`)

**5.1 Valid Delete**
```
DELETE /api/v1/poi/{po_id}/items/{po_item_id}
Expected: 200 — {"message": "Purchase order item deleted successfully"}
```

**5.2 Non-existent Item**
```
DELETE /api/v1/poi/{po_id}/items/non-existent-id
Expected: 404 — {"detail": "PO item not found or access denied"}
```

**5.3 Soft Delete Verification**
```
1. DELETE /api/v1/poi/{po_id}/items/{po_item_id}  → 200
2. GET    /api/v1/poi/{po_id}/items/{po_item_id}  → 404
```
