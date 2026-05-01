# Invoice Items API Test Cases
**Base URL:** `/api/v1/invoice-items`
**Status:** ⏳ Pending
**Prerequisites:** Valid `invoice_id`, valid `product_id`

---

## 1. CREATE (POST `/`)

**1.1 Full Valid Invoice Item**
```json
{
  "invoice_id": "<invoice_id>",
  "product_id": "<product_id>",
  "quantity": 5,
  "price": 299.99
}
Expected: 201 Created
```

**1.2 Without Price**
```json
{
  "invoice_id": "<invoice_id>",
  "product_id": "<product_id>",
  "quantity": 3
}
Expected: 201 Created
```

**1.3 Missing invoice_id**
```json
{
  "product_id": "<product_id>",
  "quantity": 5
}
Expected: 422 — {"detail": "invoice_id is required"}
```

**1.4 Missing product_id**
```json
{
  "invoice_id": "<invoice_id>",
  "quantity": 5
}
Expected: 422 — {"detail": "product_id is required"}
```

**1.5 Missing quantity**
```json
{
  "invoice_id": "<invoice_id>",
  "product_id": "<product_id>"
}
Expected: 422 — {"detail": "quantity is required"}
```
**1.6 Zero or Negative Quantity**
```json
{
  "invoice_id": "<invoice_id>",
  "product_id": "<product_id>",
  "quantity": 0
}
Expected: 409 (DB check constraint — quantity must be > 0)
```

**1.7 Invalid invoice_id**
```json
{
  "invoice_id": "non-existent-invoice",
  "product_id": "<product_id>",
  "quantity": 2
}
Expected: 409 — {"detail": "Invalid invoice_id or product_id."}
```

---

## 2. LIST (GET `/`)

**2.1 List All**
```
GET /api/v1/invoice-items
Expected: 200 — Array of invoice item objects
```

**2.2 Filter by invoice_id**
```
GET /api/v1/invoice-items?invoice_id=<invoice_id>
Expected: 200 — Items for that invoice only
```

**2.3 Pagination**
```
GET /api/v1/invoice-items?offset=0&limit=5
Expected: 200 — Max 5 items
```

---

## 3. GET Single (GET `/{invoice_item_id}`)

**3.1 Valid ID**
```
GET /api/v1/invoice-items/{invoice_item_id}
Expected: 200 — Invoice item object
```

**3.2 Invalid ID**
```
GET /api/v1/invoice-items/non-existent-id
Expected: 404 — {"detail": "Invoice item not found"}
```

---

## 4. UPDATE (PUT `/{invoice_item_id}`)

**4.1 Update Quantity and Price**
```json
{
  "quantity": 10,
  "price": 249.99
}
Expected: 200 — Updated invoice item object
```

**4.2 Non-existent Item**
```
PUT /api/v1/invoice-items/non-existent-id
Expected: 404 — {"detail": "Invoice item not found or access denied"}
```

---

## 5. DELETE (DELETE `/{invoice_item_id}`)

**5.1 Valid Delete**
```
DELETE /api/v1/invoice-items/{invoice_item_id}
Expected: 200 — {"message": "Invoice item deleted successfully"}
```

**5.2 Non-existent Item**
```
DELETE /api/v1/invoice-items/non-existent-id
Expected: 404 — {"detail": "Invoice item not found or access denied"}
```

**5.3 Soft Delete Verification**
```
1. DELETE /api/v1/invoice-items/{invoice_item_id}  → 200
2. GET    /api/v1/invoice-items/{invoice_item_id}  → 404
```
