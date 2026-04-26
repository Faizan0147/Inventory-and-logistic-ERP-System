# Products API Test Cases
**Base URL:** `/api/v1/products`
**Status:** ✅ Tested
**Prerequisites:** Valid `supplier_id`, optional `category_id`

---

## 1. CREATE (POST `/`)

**1.1 Full Valid Product**
```json
{
  "supplier_id": "<supplier_id>",
  "category_id": "<category_id>",
  "product_name": "Laptop Dell XPS 15",
  "description": "High-performance laptop",
  "sku": "DELL-XPS15-001",
  "price": 1299.99,
  "cost_price": 999.99,
  "weight": 2.5,
  "status": "Active"
}
Expected: 201 Created
```

**1.2 Minimum Required Fields**
```json
{
  "supplier_id": "<supplier_id>",
  "product_name": "Basic Product",
  "sku": "BASIC-001",
  "price": 99.99
}
Expected: 201 Created
```

**1.3 Duplicate SKU**
```json
{
  "supplier_id": "<supplier_id>",
  "product_name": "Another Product",
  "sku": "DELL-XPS15-001"
}
Expected: 409 — {"detail": "A product with SKU 'DELL-XPS15-001' already exists."}
```

**1.4 Missing product_name**
```json
{
  "supplier_id": "<supplier_id>",
  "sku": "TEST-001"
}
Expected: 422 — {"detail": "product_name is required"}
```

**1.5 Missing sku**
```json
{
  "supplier_id": "<supplier_id>",
  "product_name": "Test Product"
}
Expected: 422 — {"detail": "sku is required"}
```

**1.6 Invalid supplier_id**
```json
{
  "supplier_id": "non-existent-supplier",
  "product_name": "Test",
  "sku": "TEST-002"
}
Expected: 409 — {"detail": "Invalid supplier_id or category_id."}
```

**1.7 Negative Price**
```json
{
  "supplier_id": "<supplier_id>",
  "product_name": "Test",
  "sku": "TEST-003",
  "price": -50.00
}
Expected: 409 — {"detail": "Invalid value: price and cost_price must be 0 or greater."}
```

---

## 2. LIST (GET `/`)

**2.1 List All**
```
GET /api/v1/products
Expected: 200 — Array of product objects
```

**2.2 Pagination**
```
GET /api/v1/products?offset=0&limit=5
Expected: 200 — Max 5 products
```

---

## 3. GET Single (GET `/{product_id}`)

**3.1 Valid ID**
```
GET /api/v1/products/{product_id}
Expected: 200 — Product object
```

**3.2 Invalid ID**
```
GET /api/v1/products/non-existent-id
Expected: 404 — {"detail": "Product not found"}
```

---

## 4. UPDATE (PUT `/{product_id}`)

**4.1 Valid Update**
```json
{
  "product_name": "Laptop Dell XPS 15 Updated",
  "price": 1399.99,
  "status": "Inactive"
}
Expected: 200 — Updated product object
```

**4.2 Duplicate SKU on Update**
```json
{ "sku": "EXISTING-SKU" }
Expected: 409 — {"detail": "A product with SKU 'EXISTING-SKU' already exists."}
```

**4.3 Non-existent Product**
```
PUT /api/v1/products/non-existent-id
Expected: 404 — {"detail": "Product not found or access denied"}
```

---

## 5. DELETE (DELETE `/{product_id}`)

**5.1 Valid Delete**
```
DELETE /api/v1/products/{product_id}
Expected: 200 — {"message": "Product deleted successfully"}
```

**5.2 Non-existent Product**
```
DELETE /api/v1/products/non-existent-id
Expected: 404 — {"detail": "Product not found"}
```

**5.3 Soft Delete Verification**
```
1. DELETE /api/v1/products/{product_id}  → 200
2. GET    /api/v1/products/{product_id}  → 404
```
