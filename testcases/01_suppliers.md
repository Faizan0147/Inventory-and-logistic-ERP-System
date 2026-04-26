# Suppliers API Test Cases
**Base URL:** `/api/v1/suppliers`
**Status:** ✅ Tested

---

## 1. CREATE (POST `/`)

**1.1 Valid Supplier**
```json
POST /api/v1/suppliers
Headers: Authorization: Bearer <token>
Body:
{
  "supplier_name": "ACME Supplies",
  "contact_email": "contact@acmesupplies.com",
  "contact_phone": "+1234567890",
  "address": "123 Warehouse Street, Dubai, UAE",
  "status": "Active"
}
Expected: 201 Created
```

**1.2 Minimum Required Fields**
```json
{
  "supplier_name": "Basic Supplier"
}
Expected: 201 Created
```

**1.3 Missing supplier_name**
```json
{
  "contact_email": "test@test.com",
  "contact_phone": "+1234567890"
}
Expected: 422 — {"detail": "supplier_name is required"}
```

**1.4 Unauthorized**
```
No Authorization header
Expected: 401 Unauthorized
```

---

## 2. LIST (GET `/`)

**2.1 List All**
```
GET /api/v1/suppliers
Expected: 200 — Array of supplier objects
```

**2.2 Pagination**
```
GET /api/v1/suppliers?offset=0&limit=5
Expected: 200 — Max 5 suppliers
```

**2.3 SUPPLIER Role - Scoped Access**
```
Headers: Authorization: Bearer <supplier_token>
Expected: 200 — Only suppliers belonging to that user
```

**2.4 ADMIN Role - Full Access**
```
Headers: Authorization: Bearer <admin_token>
Expected: 200 — All suppliers
```

---

## 3. GET Single (GET `/{supplier_id}`)

**3.1 Valid ID**
```
GET /api/v1/suppliers/{supplier_id}
Expected: 200 — Supplier object
```

**3.2 Invalid ID**
```
GET /api/v1/suppliers/non-existent-id
Expected: 404 — {"detail": "Supplier not found or access denied"}
```

**3.3 Deleted Supplier**
```
GET /api/v1/suppliers/{deleted_supplier_id}
Expected: 404 — {"detail": "Supplier not found or access denied"}
```

---

## 4. UPDATE (PUT `/{supplier_id}`)

**4.1 Valid Update**
```json
PUT /api/v1/suppliers/{supplier_id}
Body:
{
  "supplier_name": "ACME Supplies Updated",
  "contact_phone": "+9876543210",
  "status": "Inactive"
}
Expected: 200 — Updated supplier object
```

**4.2 Partial Update**
```json
{ "status": "Inactive" }
Expected: 200
```

**4.3 Non-existent Supplier**
```
PUT /api/v1/suppliers/non-existent-id
Expected: 404 — {"detail": "Supplier not found or access denied"}
```

---

## 5. DELETE (DELETE `/{supplier_id}`)

**5.1 Valid Delete**
```
DELETE /api/v1/suppliers/{supplier_id}
Expected: 200 — {"message": "Supplier deleted successfully"}
```

**5.2 Non-existent Supplier**
```
DELETE /api/v1/suppliers/non-existent-id
Expected: 404 — {"detail": "Supplier not found or access denied"}
```

**5.3 Soft Delete Verification**
```
1. DELETE /api/v1/suppliers/{supplier_id}  → 200
2. GET    /api/v1/suppliers/{supplier_id}  → 404
```
