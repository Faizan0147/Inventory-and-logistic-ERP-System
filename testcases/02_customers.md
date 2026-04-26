# Customers API Test Cases
**Base URL:** `/api/v1/customers`
**Status:** ✅ Tested

---

## 1. CREATE (POST `/`)

**1.1 Full Valid Customer**
```json
{
  "customer_name": "ABC Corporation",
  "contact_person": "John Doe",
  "email": "contact@abccorp.com",
  "phone": "+1234567890",
  "address": "456 Business Ave, Dubai, UAE",
  "customer_type": "Business"
}
Expected: 201 Created
```

**1.2 Minimum Required Fields**
```json
{
  "customer_name": "Simple Customer"
}
Expected: 201 Created
```

**1.3 Duplicate Email**
```json
{
  "customer_name": "XYZ Company",
  "email": "contact@abccorp.com"
}
Expected: 409 — {"detail": "A customer with email 'contact@abccorp.com' already exists."}
```

**1.4 Missing customer_name**
```json
{
  "email": "test@test.com",
  "customer_type": "Individual"
}
Expected: 422 — {"detail": "customer_name is required"}
```

**1.5 Invalid customer_type**
```json
{
  "customer_name": "Test",
  "customer_type": "Corporate"
}
Expected: 422
```

---

## 2. LIST (GET `/`)

**2.1 List All**
```
GET /api/v1/customers
Expected: 200 — Array of customer objects
```

**2.2 Pagination**
```
GET /api/v1/customers?offset=0&limit=5
Expected: 200 — Max 5 customers
```

**2.3 SUPPLIER Role - Scoped**
```
Headers: Authorization: Bearer <supplier_token>
Expected: 200 — Only that supplier's customers
```

---

## 3. GET Single (GET `/{customer_id}`)

**3.1 Valid ID**
```
GET /api/v1/customers/{customer_id}
Expected: 200 — Customer object
```

**3.2 Invalid ID**
```
GET /api/v1/customers/non-existent-id
Expected: 404 — {"detail": "Customer not found"}
```

**3.3 Deleted Customer**
```
GET /api/v1/customers/{deleted_customer_id}
Expected: 404 — {"detail": "Customer not found"}
```

---

## 4. UPDATE (PUT `/{customer_id}`)

**4.1 Valid Update**
```json
{
  "customer_name": "ABC Corporation Updated",
  "phone": "+9876543210",
  "customer_type": "Individual"
}
Expected: 200 — Updated customer object
```

**4.2 Partial Update**
```json
{ "address": "New Address, Abu Dhabi" }
Expected: 200
```

**4.3 Duplicate Email on Update**
```json
{ "email": "existing@email.com" }
Expected: 409 — {"detail": "A customer with email 'existing@email.com' already exists."}
```

**4.4 Non-existent Customer**
```
PUT /api/v1/customers/non-existent-id
Expected: 404 — {"detail": "Customer not found or access denied"}
```

---

## 5. DELETE (DELETE `/{customer_id}`)

**5.1 Valid Delete**
```
DELETE /api/v1/customers/{customer_id}
Expected: 200 — {"message": "Customer deleted successfully"}
```

**5.2 Non-existent Customer**
```
DELETE /api/v1/customers/non-existent-id
Expected: 404 — {"detail": "Customer not found or access denied"}
```

**5.3 Soft Delete Verification**
```
1. DELETE /api/v1/customers/{customer_id}  → 200
2. GET    /api/v1/customers/{customer_id}  → 404
```
