# RBAC Query Enforcement Review Prompt

## Purpose

This document defines how to review and fix all database queries to correctly enforce Role-Based Access Control (RBAC).

Current Roles:

* ADMIN
* SUPPLIER

Goal:

Ensure every query returns only the data allowed for the logged-in user's role.

Missing role filters can expose sensitive supplier data. This must be treated as a security issue.

---

# Part 1 — RBAC Rules Definition

These rules must be applied consistently across all queries.

## ADMIN Role

ADMIN users:

* Can view all records
* Can access all suppliers
* Can access all warehouses
* Can view all inventory
* Can view all purchase orders
* Can view all invoices
* Can view all shipments

ADMIN queries:

No supplier filtering required.

---

## SUPPLIER Role

SUPPLIER users:

Must only access:

* Their own supplier data
* Their own products
* Their own purchase orders
* Their own invoices
* Their own shipments
* Their own inventory records

SUPPLIER queries must include:

```sql
WHERE supplier_id = :user
```

Or equivalent join-based filtering.

Never allow supplier-level unrestricted access.

---

# Part 2 — Required Code Review Task

Review the full codebase.

Focus on:

* SQL queries
* ORM queries
* Query builders
* Stored procedures
* Report queries
* Analytics queries

Find all queries that:

* select data
* update data
* delete data

Check whether they enforce role-based filtering.

---

# Part 3 — Identify Missing WHERE Conditions

Find queries missing:

```sql
WHERE user_id = current user_id
```

Common failure cases:

* SELECT * queries
* dashboard summary queries
* analytics queries
* JOIN queries without supplier filter
* count queries without role filter

Example of unsafe query:

```sql
SELECT * FROM purchase_orders;
```

Correct version:

```sql
SELECT *
FROM purchase_orders
WHERE user_id = :current_user_id;
```

---

# Part 4 — JOIN Query Security Review

Check queries using JOIN.

Ensure filtering is applied on the correct table.

Unsafe example:

```sql
SELECT *
FROM purchase_orders po
JOIN products p
ON p.product_id = po.product_id;
```

Correct version:

```sql
SELECT *
FROM purchase_orders po
JOIN products p
ON p.product_id = po.product_id
WHERE po.user_id = :current_user_id;
```

Filtering only on product table is not sufficient.

Always filter on ownership table.

---

# Part 5 — Aggregation Query Protection

Check queries using:

* COUNT
* SUM
* GROUP BY

Example risk:

```sql
SELECT COUNT(*) FROM shipments;
```

This exposes global totals.

Correct:

```sql
SELECT COUNT(*)
FROM shipments
WHERE supplier_id = :current_supplier_id;
```

---

# Part 6 — Update and Delete Query Protection

Check UPDATE queries.

Unsafe:

```sql
UPDATE products
SET price = 100;
```

Correct:

```sql
UPDATE products
SET price = 100
WHERE user_id = :current_user_id;
```

Same applies to DELETE queries.

Never allow unrestricted updates.

---

# Part 7 — Conversational Query Security

System supports natural language queries converted to SQL.

Risk:

Generated SQL may ignore RBAC rules.

Required rule:

All generated SQL must pass through a security layer.

Before execution:

Validate:

* Role
* Supplier ownership

Required enforcement:

Always append:

```sql
WHERE supplier_id = :current_supplier_id
```

Or equivalent secure filter.

Never run raw generated SQL directly.

---

# Part 8 — Middleware Enforcement Requirement

RBAC filtering must not rely only on frontend logic.

Required:

Implement server-side middleware that:

* detects user role
* injects supplier filter automatically
* blocks unsafe queries

Required validation:

Reject queries missing supplier filter.

Return error if unsafe query detected.

---

# Part 9 — Required Code Fix Actions

Perform automatic fixes where possible.

Required fixes:

1 — Add supplier filtering to SELECT queries
2 — Add supplier filtering to UPDATE queries
3 — Add supplier filtering to DELETE queries
4 — Secure JOIN queries
5 — Secure aggregate queries

If unsafe query found:

Modify query.

Do not only report it.

---

# Part 10 — Required Output Report

Generate Markdown report.

Include:

## Files Modified

List all files changed.

---

## Queries Fixed

For each query:

Show:

Unsafe version
Corrected version

---

## Remaining Risk Areas

List areas that still require manual review.

---

# Part 11 — Required Schema Validation

Verify supplier ownership exists.

Check that these tables include:

```sql
supplier_id
```

Required tables:

* products
* purchase_orders
* invoices
* shipments
* inventory

If missing:

Report schema issue.

---

# Part 12 — Testing Requirements

After fixes:

Run test cases.

Required tests:

SUPPLIER user:

* cannot see other supplier data
* cannot update other supplier data
* cannot delete other supplier data

ADMIN user:

* can access all records

All tests must pass.

---

# Part 13 — Final Rule

Never trust role filtering done in UI.

All access control must be enforced at query level.

No exceptions.
