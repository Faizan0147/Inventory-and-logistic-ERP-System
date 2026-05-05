# Invoices API Test Cases
**Base URL:** `/api/v1/invoice`
**Status:** 🔄 Ready for Testing

---

## Prerequisites
- Valid supplier_id (from suppliers table)
- Valid po_id (optional, from purchase_orders table)
- Valid authentication token (ADMIN or SUPPLIER role)

---

## 1. CREATE (POST `/`)

**1.1 Valid Invoice with All Fields**
```json
POST /api/v1/invoice
Headers: Authorization: Bearer <token>
Body:
{
  "supplier_id": "<valid_supplier_id>",
  "po_id": "<valid_po_id>",
  "invoice_number": "INV-2026-001",
  "invoice_date": "2026-05-05",
  "total_amount": 1500.00,
  "status": "Draft"
}
Expected: 201 Created
Response should include:
- invoice_id
- user_id (from token)
- supplier (nested object with supplier details)
- purchase_order (nested object with PO details)
- created_at, updated_at, created_by, updated_by
```

**1.2 Minimum Required Fields (Only supplier_id)**
```json
{
  "supplier_id": "<valid_supplier_id>"
}
Expected: 201 Created
Note: All other fields are optional
```

**1.3 Invoice Without Purchase Order**
```json
{
  "supplier_id": "<valid_supplier_id>",
  "invoice_number": "INV-2026-002",
  "invoice_date": "2026-05-05",
  "total_amount": 2500.00,
  "status": "Pending"
}
Expected: 201 Created
Note: po_id is optional
```

**1.4 Valid Status Values**
```json
Test each status separately:
- "Draft"
- "Pending"
- "Paid"
- "Overdue"
- "Cancelled"
Expected: 201 Created for each
```

**1.5 Missing supplier_id**
```json
{
  "invoice_number": "INV-2026-003",
  "invoice_date": "2026-05-05",
  "total_amount": 1000.00
}
Expected: 422 — {"detail": "supplier_id is required"}
```

**1.6 Invalid supplier_id (Non-existent)**
```json
{
  "supplier_id": "non-existent-supplier-id",
  "invoice_number": "INV-2026-004"
}
Expected: 409 — {"detail": "Invalid supplier_id or po_id."}
```

**1.7 Invalid po_id (Non-existent)**
```json
{
  "supplier_id": "<valid_supplier_id>",
  "po_id": "non-existent-po-id",
  "invoice_number": "INV-2026-005"
}
Expected: 409 — {"detail": "Invalid supplier_id or po_id."}
```

**1.8 Invalid Status Value**
```json
{
  "supplier_id": "<valid_supplier_id>",
  "status": "InvalidStatus"
}
Expected: 500 or validation error
Note: Status must be one of: Draft, Pending, Paid, Overdue, Cancelled
```

**1.9 Negative Total Amount**
```json
{
  "supplier_id": "<valid_supplier_id>",
  "total_amount": -100.00
}
Expected: 201 Created (no constraint on negative values in schema)
Note: Consider adding CHECK constraint if business logic requires positive amounts
```

**1.10 Unauthorized Request**
```
POST /api/v1/invoice
No Authorization header
Expected: 401 Unauthorized
```

**1.11 Multi-Tenant Isolation**
```
1. User A creates invoice with supplier_id from User A
   Expected: 201 Created
2. User B tries to create invoice with same supplier_id (belongs to User A)
   Expected: 409 — Foreign key violation (if supplier doesn't exist for User B)
```

---

## 2. LIST (GET `/`)

**2.1 List All Invoices**
```
GET /api/v1/invoice
Headers: Authorization: Bearer <token>
Expected: 200 — Array of invoice objects with nested supplier and purchase_order
```

**2.2 Pagination - Default**
```
GET /api/v1/invoice
Expected: 200 — Max 100 invoices (default limit)
```

**2.3 Pagination - Custom Offset and Limit**
```
GET /api/v1/invoice?offset=0&limit=5
Expected: 200 — Max 5 invoices
```

**2.4 Pagination - Large Offset**
```
GET /api/v1/invoice?offset=1000&limit=10
Expected: 200 — Empty array if no more records
```

**2.5 SUPPLIER Role - Scoped Access**
```
Headers: Authorization: Bearer <supplier_token>
Expected: 200 — Only invoices belonging to that user (user_id filter applied)
```

**2.6 ADMIN Role - Full Access**
```
Headers: Authorization: Bearer <admin_token>
Expected: 200 — All invoices across all users
```

**2.7 Empty Result**
```
New user with no invoices
Expected: 200 — []
```

**2.8 Verify Soft Delete**
```
Deleted invoices should NOT appear in list
Expected: Only active invoices (deleted = FALSE)
```

---

## 3. GET Single (GET `/{invoice_id}`)

**3.1 Valid Invoice ID**
```
GET /api/v1/invoice/{invoice_id}
Headers: Authorization: Bearer <token>
Expected: 200 — Invoice object with:
- All invoice fields
- supplier (nested object)
- purchase_order (nested object if po_id exists)
```

**3.2 Non-existent Invoice ID**
```
GET /api/v1/invoice/non-existent-id
Expected: 404 — {"detail": "Invoice not found"}
```

**3.3 Deleted Invoice**
```
GET /api/v1/invoice/{deleted_invoice_id}
Expected: 404 — {"detail": "Invoice not found"}
```

**3.4 Multi-Tenant Isolation (SUPPLIER Role)**
```
User A tries to access User B's invoice
GET /api/v1/invoice/{user_b_invoice_id}
Headers: Authorization: Bearer <user_a_token>
Expected: 404 — {"detail": "Invoice not found"}
```

**3.5 ADMIN Access to Any Invoice**
```
Admin tries to access any user's invoice
GET /api/v1/invoice/{any_invoice_id}
Headers: Authorization: Bearer <admin_token>
Expected: 200 — Invoice object (admin has full access)
```

**3.6 Unauthorized Request**
```
GET /api/v1/invoice/{invoice_id}
No Authorization header
Expected: 401 Unauthorized
```

---

## 4. UPDATE (PUT `/{invoice_id}`)

**4.1 Valid Full Update**
```json
PUT /api/v1/invoice/{invoice_id}
Headers: Authorization: Bearer <token>
Body:
{
  "supplier_id": "<different_valid_supplier_id>",
  "po_id": "<different_valid_po_id>",
  "invoice_number": "INV-2026-UPDATED",
  "invoice_date": "2026-05-10",
  "total_amount": 3000.00,
  "status": "Paid"
}
Expected: 200 — Updated invoice object
Verify: updated_at timestamp changed, updated_by set to current user
```

**4.2 Partial Update - Status Only**
```json
{
  "status": "Paid"
}
Expected: 200 — Only status updated, other fields unchanged
```

**4.3 Partial Update - Total Amount Only**
```json
{
  "total_amount": 2000.00
}
Expected: 200
```

**4.4 Partial Update - Invoice Number**
```json
{
  "invoice_number": "INV-2026-REVISED"
}
Expected: 200
```

**4.5 Update with Invalid supplier_id**
```json
{
  "supplier_id": "non-existent-supplier-id"
}
Expected: 409 — {"detail": "Invalid supplier_id or po_id."}
```

**4.6 Update with Invalid po_id**
```json
{
  "po_id": "non-existent-po-id"
}
Expected: 409 — {"detail": "Invalid supplier_id or po_id."}
```

**4.7 Update Non-existent Invoice**
```
PUT /api/v1/invoice/non-existent-id
Body: { "status": "Paid" }
Expected: 404 — {"detail": "Invoice not found"}
```

**4.8 Update Deleted Invoice**
```
PUT /api/v1/invoice/{deleted_invoice_id}
Body: { "status": "Paid" }
Expected: 404 — {"detail": "Invoice not found"}
```

**4.9 Multi-Tenant Isolation (SUPPLIER Role)**
```
User A tries to update User B's invoice
PUT /api/v1/invoice/{user_b_invoice_id}
Headers: Authorization: Bearer <user_a_token>
Body: { "status": "Paid" }
Expected: 404 — {"detail": "Invoice not found"}
```

**4.10 ADMIN Can Update Any Invoice**
```
PUT /api/v1/invoice/{any_invoice_id}
Headers: Authorization: Bearer <admin_token>
Body: { "status": "Paid" }
Expected: 200 — Updated invoice
```

**4.11 Update with Empty Body**
```json
{}
Expected: 200 — No changes made (all fields are optional in update)
```

**4.12 Remove Optional Fields (Set to null)**
```json
{
  "po_id": null,
  "invoice_number": null
}
Expected: 200 — Fields set to null
Note: Verify if COALESCE in SQL preserves null or keeps existing value
```

---

## 5. DELETE (DELETE `/{invoice_id}`)

**5.1 Valid Delete**
```
DELETE /api/v1/invoice/{invoice_id}
Headers: Authorization: Bearer <token>
Expected: 200 — {"message": "Invoice deleted successfully"}
```

**5.2 Verify Soft Delete**
```
1. DELETE /api/v1/invoice/{invoice_id}  → 200
2. GET    /api/v1/invoice/{invoice_id}  → 404
3. Check database: deleted = TRUE, updated_at changed, updated_by set
```

**5.3 Delete Non-existent Invoice**
```
DELETE /api/v1/invoice/non-existent-id
Expected: 404 — {"detail": "Invoice not found"}
```

**5.4 Delete Already Deleted Invoice**
```
DELETE /api/v1/invoice/{already_deleted_invoice_id}
Expected: 404 — {"detail": "Invoice not found"}
```

**5.5 Multi-Tenant Isolation (SUPPLIER Role)**
```
User A tries to delete User B's invoice
DELETE /api/v1/invoice/{user_b_invoice_id}
Headers: Authorization: Bearer <user_a_token>
Expected: 404 — {"detail": "Invoice not found"}
```

**5.6 ADMIN Can Delete Any Invoice**
```
DELETE /api/v1/invoice/{any_invoice_id}
Headers: Authorization: Bearer <admin_token>
Expected: 200 — {"message": "Invoice deleted successfully"}
```

**5.7 Cascade Effect on Invoice Items**
```
1. Create invoice with invoice_items
2. DELETE /api/v1/invoice/{invoice_id}
3. Check invoice_items table
Expected: Invoice items should be cascade deleted (ON DELETE CASCADE)
```

---

## 6. Edge Cases & Business Logic

**6.1 Invoice with Future Date**
```json
{
  "supplier_id": "<valid_supplier_id>",
  "invoice_date": "2027-12-31"
}
Expected: 201 Created (no date validation in schema)
```

**6.2 Invoice with Past Date**
```json
{
  "supplier_id": "<valid_supplier_id>",
  "invoice_date": "2020-01-01"
}
Expected: 201 Created
```

**6.3 Large Total Amount**
```json
{
  "supplier_id": "<valid_supplier_id>",
  "total_amount": 9999999999.99
}
Expected: 201 Created (NUMERIC(12,2) supports up to 10 digits before decimal)
```

**6.4 Total Amount Exceeds Precision**
```json
{
  "supplier_id": "<valid_supplier_id>",
  "total_amount": 99999999999.99
}
Expected: 500 — Database error (exceeds NUMERIC(12,2))
```

**6.5 Decimal Precision**
```json
{
  "supplier_id": "<valid_supplier_id>",
  "total_amount": 100.999
}
Expected: 201 Created (rounded to 100.99 or 101.00 depending on DB rounding)
```

**6.6 Invoice Number Uniqueness**
```
1. Create invoice with invoice_number "INV-001"
2. Create another invoice with same invoice_number "INV-001"
Expected: Both succeed (no unique constraint on invoice_number)
Note: Consider adding unique constraint if business requires unique invoice numbers
```

**6.7 Supplier and PO Belong to Different Users**
```json
{
  "supplier_id": "<user_a_supplier_id>",
  "po_id": "<user_b_po_id>"
}
Expected: May succeed but creates data inconsistency
Note: Consider adding validation to ensure supplier and PO belong to same user
```

---

## 7. Response Validation

**7.1 Verify Nested Supplier Object**
```
GET /api/v1/invoice/{invoice_id}
Expected response includes:
"supplier": {
  "supplier_id": "...",
  "supplier_name": "...",
  "contact_email": "...",
  "contact_phone": "..."
}
```

**7.2 Verify Nested Purchase Order Object**
```
GET /api/v1/invoice/{invoice_id_with_po}
Expected response includes:
"purchase_order": {
  "po_id": "...",
  "order_number": "...",
  "order_date": "...",
  "status": "..."
}
```

**7.3 Verify Null Purchase Order When po_id is Null**
```
GET /api/v1/invoice/{invoice_id_without_po}
Expected: "purchase_order": null
```

**7.4 Verify Timestamps**
```
All responses should include:
- created_at (ISO 8601 format)
- updated_at (ISO 8601 format)
- created_by (user_id)
- updated_by (user_id)
```

---

## 8. Performance & Load Testing

**8.1 List Large Dataset**
```
GET /api/v1/invoice?limit=1000
Expected: 200 — Response time < 2 seconds
```

**8.2 Concurrent Creates**
```
Multiple users creating invoices simultaneously
Expected: All succeed with unique invoice_ids
```

**8.3 Concurrent Updates to Same Invoice**
```
Two users update same invoice simultaneously
Expected: Last write wins, both get 200 (or implement optimistic locking)
```

---

## Notes
- All endpoints require authentication (Bearer token)
- SUPPLIER role: Can only access their own invoices (user_id filter)
- ADMIN role: Can access all invoices (no user_id filter)
- Soft delete: deleted = TRUE, records remain in database
- Foreign key constraints: supplier_id (CASCADE), po_id (SET NULL)
- Status values: Draft, Pending, Paid, Overdue, Cancelled
- invoice_number: No unique constraint (consider adding if needed)
- Multi-tenant isolation: Enforced via user_id field
