# RBAC Query Enforcement Review Report

## Summary

Full codebase audit performed against the RBAC rules defined in `RBAC_QUERY_REVIEW_PROMPT.md`.
Session context provides: `user_id`, `role`, `supplier_id`.
Filtering uses `supplier_id` on owned-resource tables and `supplier_id` on the `users` table to scope company membership.

---

## Schema Audit — `supplier_id` / `user_id` Column Presence

| Table                  | `supplier_id` | Notes |
|------------------------|---------------|-------|
| `users`                | ✅ Present     | Links SUPPLIER user to their company |
| `suppliers`            | ✅ PK          | Is the supplier entity |
| `products`             | ✅ Present     | Ownership column |
| `inventory`            | ✅ Present     | Added explicitly for RBAC |
| `purchase_orders`      | ✅ Present     | Ownership column |
| `invoices`             | ✅ Present     | Ownership column |
| `shipments`            | ✅ Present     | Added explicitly for RBAC |
| `purchase_order_items` | ❌ Missing     | Protected via JOIN to `purchase_orders.supplier_id` |
| `invoice_items`        | ❌ Missing     | Protected via JOIN to `invoices.supplier_id` |
| `warehouses`           | ❌ Missing     | Global shared resource — acceptable |
| `categories`           | ❌ Missing     | Global shared resource — acceptable |
| `customers`            | ❌ Missing     | Global shared resource — acceptable |

`purchase_order_items` and `invoice_items` do not need a direct `supplier_id` column because all queries
filter through their parent table via subquery or JOIN — this is correctly implemented.

---

## Files Modified

- `app/repositories/users_repo.py`
- `app/controllers/user.py`

---

## Queries Fixed

### 1. `users_repo.get_user` — Missing supplier_id filter

**Unsafe (before):**
```sql
SELECT ... FROM users WHERE user_id = $1 AND deleted = FALSE
```
A SUPPLIER could retrieve any user in the system by ID.

**Fixed:**
```sql
SELECT ... FROM users WHERE user_id = $1 AND deleted = FALSE
-- AND supplier_id = $2  (appended when caller is SUPPLIER)
```

---

### 2. `users_repo.list_users` — Missing supplier_id filter

**Unsafe (before):**
```sql
SELECT ... FROM users WHERE deleted = FALSE ORDER BY name LIMIT $1 OFFSET $2
```
A SUPPLIER could enumerate all users across all companies.

**Fixed:**
```sql
SELECT ... FROM users WHERE deleted = FALSE
-- AND supplier_id = $3  (appended when caller is SUPPLIER)
ORDER BY name LIMIT $1 OFFSET $2
```

---

### 3. `users_repo.update_user` — No ownership guard at query level

**Unsafe (before):**
```sql
UPDATE users SET ... WHERE user_id = $9 AND deleted = FALSE
```
Controller blocked cross-user updates by role check, but the repo had no DB-level guard.

**Fixed:**
```sql
UPDATE users SET ... WHERE user_id = $9 AND deleted = FALSE
-- AND supplier_id = $10  (appended when caller is SUPPLIER)
```

---

### 4. `users_repo.delete_user` — No ownership guard at query level

**Unsafe (before):**
```sql
UPDATE users SET deleted = TRUE ... WHERE user_id = $1 AND deleted = FALSE
```

**Fixed:**
```sql
UPDATE users SET deleted = TRUE ... WHERE user_id = $1 AND deleted = FALSE
-- AND supplier_id = $3  (appended when caller is SUPPLIER)
```

---

### 5. `controllers/user.py` — update_user / delete_user not passing supplier_id to repo

Controller now extracts `supplier_id` from session and passes it to both `update_user` and `delete_user`
so the DB-level guard is active.

---

## Already Correctly Enforced (No Changes Needed)

| Resource | SELECT | UPDATE | DELETE | Notes |
|---|---|---|---|---|
| `products` | ✅ | ✅ | ✅ | supplier_id filter in all repo operations |
| `inventory` | ✅ | ✅ | ✅ | supplier_id filter in all repo operations |
| `purchase_orders` | ✅ | ✅ | ✅ | supplier_id filter in all repo operations |
| `invoices` | ✅ | ✅ | ✅ | supplier_id filter in all repo operations |
| `shipments` | ✅ | ✅ | ✅ | supplier_id filter in all repo operations |
| `purchase_order_items` | ✅ | ✅ | ✅ | JOIN-based supplier_id filter via purchase_orders |
| `invoice_items` | ✅ | ✅ | ✅ | JOIN-based supplier_id filter via invoices |
| `suppliers` | ✅ | ✅ | ✅ | SUPPLIER sees only own; create/delete SUPERADMIN-only |

---

## Remaining Risk Areas (Manual Review Required)

### 1. `customers`, `warehouses`, `categories` — Global Resources
These tables have no `supplier_id` and are treated as shared/global resources.
All authenticated users (ADMIN and SUPPLIER) can read and write them.

**Action required:** Confirm with product owner whether these should remain global or be scoped per supplier.
If supplier-scoped, a `supplier_id` column must be added to each table and filtering implemented.

### 2. NL→SQL / Conversational Query Feature
If a natural language to SQL feature is implemented in the future, all generated SQL must be
validated before execution. Required: append `AND supplier_id = :current_supplier_id` to any
generated query that touches supplier-owned tables. Never execute raw generated SQL directly.

### 3. Admin `list_pending_requests`
`auth_repo.list_pending_requests` returns all registration requests with no role filter.
This is currently only accessible to SUPERADMIN (enforced at route level) — verify route guard is in place.

### 4. `users` table — SUPERADMIN role check
The `update_user` and `delete_user` controller logic was changed to use `SUPPLIER`-scoped checks.
Ensure SUPERADMIN routes are still protected by `require_role("SUPERADMIN")` at the route layer
so admins retain full access.

---

## Schema Issues

None critical. The following are noted:

- `purchase_order_items` and `invoice_items` have no direct `supplier_id` — **acceptable**, ownership
  is enforced via JOIN/subquery through parent tables.
- `warehouses`, `categories`, `customers` have no `supplier_id` — **by design** as global resources,
  but should be confirmed with product owner.
