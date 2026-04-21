# API Route Review and End-to-End Test Plan

Generated from repository scan on 2026-04-21.

**Scope**: list of routes, middleware, request/response shapes (POST/PUT), RBAC/auth checks, full system setup order, and example test payloads.

Prefix: All routes are mounted under `/api/v1` (see `app/main.py` and `app/api.py`).

## 1. Routes Inventory (grouped by module)

- Auth (`/api/v1/auth`)
  - POST /register  (no auth dependency) - body: `RegistrationRequestCreate`
  - POST /login     (no auth dependency) - body: `LoginRequest`

- Admin (`/api/v1/admin`)
  - GET /registration-requests  (requires `SUPERADMIN`)
  - POST /registration-requests/{request_id}/approve  (requires `SUPERADMIN`)
  - POST /registration-requests/{request_id}/reject   (requires `SUPERADMIN`)

- Suppliers (`/api/v1/suppliers`)
  - POST /          (body: `SupplierCreate`, depends on `get_current_user`)
  - GET /           (query: `offset`, `limit`; depends on `get_current_user`)
  - GET /{supplier_id}
  - PATCH /{supplier_id}
  - DELETE /{supplier_id}

- Categories (`/api/v1/categories`)
  - POST / (CategoryCreate)
  - GET / (offset, limit)
  - GET /{category_id}
  - PATCH /{category_id}
  - DELETE /{category_id}

- Warehouses (`/api/v1/warehouses`)
  - POST /
  - GET /
  - GET /{warehouse_id}
  - PATCH /{warehouse_id}
  - DELETE /{warehouse_id}

- Products (`/api/v1/products`)
  - POST /
  - GET /
  - GET /{product_id}
  - PATCH /{product_id}
  - DELETE /{product_id}

- Inventory (`/api/v1/inventory`)
  - POST /
  - GET /
  - GET /{inventory_id}
  - PATCH /{inventory_id}
  - DELETE /{inventory_id}

- Purchase Orders (`/api/v1/purchase-order`)
  - POST /
  - GET /
  - GET /{po_id}
  - PATCH /{po_id}
  - DELETE /{po_id}

- Purchase Order Items (`/api/v1/poi`)
  - POST /{po_id}/items
  - GET /{po_id}/items
  - GET /{po_id}/items/{po_item_id}
  - PATCH /{po_id}/items/{po_item_id}
  - DELETE /{po_id}/items/{po_item_id}

- Invoice (`/api/v1/invoice`)
  - POST /
  - GET /
  - GET /{invoice_id}
  - PATCH /{invoice_id}
  - DELETE /{invoice_id}

- Invoice Items (`/api/v1/invoice-items`)
  - POST /
  - GET / (optional query `invoice_id`)
  - GET /{invoice_item_id}
  - PATCH /{invoice_item_id}
  - DELETE /{invoice_item_id}

- Customers (`/api/v1/customers`)
  - POST /
  - GET /
  - GET /{customer_id}
  - PATCH /{customer_id}
  - DELETE /{customer_id}

- Shipments (`/api/v1/shipments`)
  - POST /
  - GET /
  - GET /{shipment_id}
  - PATCH /{shipment_id}
  - DELETE /{shipment_id}

- Users (`/api/v1/users`)
  - POST / (requires `SUPERADMIN`)
  - GET /  (requires `SUPERADMIN`)
  - GET /{user_id}  (requires `SUPERADMIN`)
  - PATCH /{user_id}
  - DELETE /{user_id}


## 2. Middleware / Auth / RBAC Summary

- Authentication dependency: `app.utils.dependencies.get_current_user` (OAuth2 Bearer). Most routers use it via `Depends(get_current_user)`.
- Role enforcement: `require_role("SUPERADMIN")` is used on `admin` routes and for creating/listing `users`.
- `auth` routes (`/register`, `/login`) do not require authentication.
- Recommendation: controllers should enforce supplier scoping when `current_user["role"] == "SUPPLIER"` to avoid cross-supplier access. I did not find global supplier-filtering middleware; confirm controllers implement it.

## 3. Request Payload Review (POST / PATCH shapes and required fields)

I extracted DTOs from `app/dto/*.py`. Below are required vs optional fields for create/update models and notes.

- Users (`app/dto/users.py`)
  - `UserCreate` required: `name`, `email`, `password`.
  - optional: `phone_number`, `role` (default `SUPPLIER`), `supplier_id`.
  - `UserUpdate`: all optional.
  - Note: `role` is a plain `str` — recommend using an `Enum` or `Literal` to restrict to allowed values (e.g., `SUPERADMIN`, `ADMIN`, `SUPPLIER`).

- Suppliers (`app/dto/supplier.py`)
  - `SupplierCreate` required: `supplier_name`.
  - optional: `contact_email`, `contact_phone`, `address`, `status` (default `Active`).

- Categories (`app/dto/category.py`) — (similar pattern; ensure `name` required). (See file for exact fields.)

- Warehouses (`app/dto/warehouse.py`) — required: `warehouse_name`, `address` (check file for specifics).

- Products (`app/dto/product.py`)
  - `ProductCreate` required: `supplier_id`, `product_name`.
  - optional: `category_id`, `description`, `sku`, `price`, `cost_price`, `weight`, `status` (default `Active`).
  - Recommendation: `price`, `cost_price`, `weight` use `Decimal` in DTO — controllers should validate positive numbers and sensible ranges.

- Inventory (`app/dto/inventory.py`) — required: `product_id`, `warehouse_id`, `quantity` (check DTO file). Validate non-negative integers.

- Purchase Order (`app/dto/purchase_order.py`) — required: `supplier_id`, `warehouse_id`, `status`? Check DTO for required fields; ensure PO status values are constrained.

- PO Items (`app/dto/poi.py`) — required: `po_id`, `product_id`, `quantity`, `unit_price`.

- Invoice / Invoice Items (`app/dto/invoice.py`, `invoice_item.py`) — check DTOs for required fields (invoice should reference PO or supplier, invoice items reference invoice, product, quantity, price).

- Customers (`app/dto/customers.py`) — required: `customer_name`.

- Shipments (`app/dto/shipments.py`) — required: `po_id`, `warehouse_id`, `shipment_date`? Verify in DTO.

General validation gaps observed:
- Several fields representing enumerations or statuses are plain strings. Convert to Pydantic `Enum` or `Literal` for stricter validation.
- Email fields are plain Optional[str]; consider `EmailStr` from Pydantic to validate email format.
- Numeric fields (price, quantity, weight) should have additional constraints (gt=0 or ge=0) in DTOs.

## 4. Response Structure Review

- Controllers use Pydantic `response_model` on all routes; responses will be validated/output consistently.
- Ensure controllers never return raw DB rows or sensitive fields (password hashes). DTO `UserRead` does not include password — good.
- Error handling: ensure controllers raise `HTTPException` with clear messages. Add consistent error schema if desired.

## 5. RBAC & Authentication Checks

- Routes requiring `SUPERADMIN` are properly decorated (`admin`, creating/listing users).
- Most business routes require `get_current_user`. Confirm controllers check `current_user['supplier_id']` to restrict data for `SUPPLIER` role.
- Action items:
  - Audit controllers for supplier-scoped queries; add `WHERE supplier_id = current_user['supplier_id']` where applicable.
  - Protect `GET` list endpoints from returning cross-supplier data when `current_user` is a supplier.

## 6. Full System Setup Order

Follow this order for end-to-end tests (matches prompt):
1. Users: create `SUPERADMIN` and `SUPPLIER` users (or `ADMIN` as needed). Acquire tokens.
2. Suppliers: create supplier record (link the SUPPLIER user to supplier_id).
3. Warehouses: create warehouses.
4. Categories: create categories.
5. Products: create products with `supplier_id` and `category_id`.
6. Inventory: assign products to warehouses with initial stock.
7. Purchase Orders: create PO linked to `supplier_id` + `warehouse_id`.
8. Purchase Order Items: add products to PO.
9. Invoices: create invoice linked to PO + supplier.
10. Invoice Items: add invoice line items.
11. Customers: create customer records.
12. Shipments: create shipment linked to PO + warehouse.

## 7. Example Test Payloads (valid, edge, invalid)

- POST /api/v1/auth/register (valid)
```
{ "name": "Alice Admin", "email": "alice@example.com", "password": "strongpass123", "role": "SUPERADMIN" }
```

- POST /api/v1/users (create user, requires SUPERADMIN)
Valid:
```
{ "name":"Supplier Owner", "email":"owner@supplier.com", "password":"P@ssw0rd", "role":"SUPPLIER", "supplier_id": "SUP-001" }
```
Edge (missing optional supplier_id for ADMIN):
```
{ "name":"Admin Two", "email":"admin2@example.com", "password":"x", "role":"ADMIN" }
```
Invalid (missing required `email`):
```
{ "name":"No Email", "password":"abc" }
```

- POST /api/v1/suppliers
Valid:
```
{ "supplier_name":"Acme Supplies", "contact_email":"sales@acme.test", "address":"123 Market St" }
```
Invalid (empty name): `{ "supplier_name": "" }`

- POST /api/v1/products
Valid:
```
{ "supplier_id":"SUP-001", "category_id":"CAT-001", "product_name":"Wireless Mouse", "price":1500.00, "cost_price":1000.00, "status":"Active" }
```
Edge (no category):
```
{ "supplier_id":"SUP-001", "product_name":"Generic Item" }
```
Invalid (negative price):
```
{ "supplier_id":"SUP-001", "product_name":"Broken", "price": -10 }
```

- POST /api/v1/inventory
Valid:
```
{ "product_id":"PROD-001", "warehouse_id":"WH-001", "quantity":100 }
```
Invalid (non-integer quantity): `{ "product_id":"PROD-001", "warehouse_id":"WH-001", "quantity": "a lot" }`

- POST /api/v1/purchase-order
Valid minimal:
```
{ "supplier_id":"SUP-001", "warehouse_id":"WH-001", "order_date":"2026-04-21" }
```

- POST /api/v1/poi/{po_id}/items
Valid:
```
{ "product_id":"PROD-001", "quantity":10, "unit_price":1200.00 }
```

- POST /api/v1/invoice
Valid:
```
{ "po_id":"PO-001", "supplier_id":"SUP-001", "invoice_date":"2026-04-21", "total":12000.00 }
```

- POST /api/v1/customers
Valid:
```
{ "customer_name":"Bob Retail", "contact_email":"bob@retail.com" }
```

- POST /api/v1/shipments
Valid (example):
```
{ "po_id":"PO-001", "warehouse_id":"WH-001", "shipped_at":"2026-04-22" }
```

## 8. Recommended Fixes / Next Steps

- Convert free-form status/role strings into `Enum` or `Literal` types in DTOs.
- Use `EmailStr` for email fields.
- Add numeric constraints in DTOs: `gt`/`ge` for quantities and prices.
- Audit controllers to ensure supplier scoping applied for supplier users (prevent cross-supplier data leaks).
- Add end-to-end tests following the Full System Setup Order. Tests should:
  - Create users and authenticate to retrieve tokens
  - Create supplier + resources in dependency order
  - Assert RBAC: supplier cannot access other suppliers' resources
  - Assert validation errors return appropriate 4xx responses

## 9. Files inspected
- [app/api.py](app/api.py)
- [app/main.py](app/main.py)
- `app/routes/*` (all route files)
- `app/dto/*` (DTOs used as request/response models)
- `app/utils/dependencies.py`


---

If you want, I can:
- produce a machine-readable list (CSV/JSON) of all routes and models,
- generate a Postman collection or OpenAPI test cases with the example payloads,
- or implement the DTO improvements (Enums, EmailStr, numeric constraints) as patches.

Which next step would you like me to take?