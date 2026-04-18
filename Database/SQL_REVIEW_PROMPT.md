# SQL Schema Review and Performance Guidelines

## Purpose

This document defines how the SQL schema should be reviewed, maintained, and optimized.

It exists to prevent long-term failures caused by:

* poor schema design
* missing indexes
* slow query performance
* uncontrolled schema growth

This system currently handles:

* Inventory
* Procurement
* Logistics

It will later expand to:

* Sales
* Customer billing
* Analytics reporting

All schema changes must consider future expansion.

---

# Part 1 — SQL Schema Review Prompt

## Instructions for Code Agent

You are reviewing a SQL schema for an Inventory and Logistics ERP system.

Current scope:

* Suppliers
* Users
* Categories
* Warehouses
* Products
* Inventory
* Purchase Orders
* Purchase Order Items
* Invoices
* Invoice Items
* Customers
* Shipments

Future scope:

* Sales Orders
* Sales Shipments
* Payments
* Revenue Analytics

Your task:

Perform a deep schema audit.

Do NOT rewrite schema.

Do NOT summarize tables.

Focus on:

* correctness
* scalability
* reliability
* performance

---

## Required Review Sections

The generated report must include:

### 1 — Critical Structural Issues

Find:

* missing foreign keys
* incorrect relationships
* broken dependencies
* nullable fields that should not be nullable

Explain:

* why issue is dangerous
* how it can fail in production
* exact schema fix

---

### 2 — Data Integrity Risks

Check:

* missing UNIQUE constraints
* duplicate risks (SKU, order numbers)
* incorrect data types
* invalid defaults

Focus on preventing:

* duplicate records
* corrupted relationships

---

### 3 — Indexing Review

Identify missing indexes.

Focus heavily on:

* foreign key columns
* search fields
* reporting columns

Mandatory index targets:

* product_id
* warehouse_id
* supplier_id
* category_id
* po_id
* invoice_id
* shipment_id

---

### 4 — Performance Risk Analysis

Assume:

* 100k products
* 1M inventory rows
* 100k purchase orders

Find:

* slow join paths
* full table scan risks
* heavy aggregation risks

---

### 5 — Missing ERP Tables

Check for absence of:

Inventory Requirements:

* inventory_transactions
* stock_adjustments
* returns

Future Sales Requirements:

* sales_orders
* sales_order_items
* payments
* customer_shipments

---

### 6 — Workflow Limitations

Check whether system supports:

* partial deliveries
* multiple shipments per order
* returns
* cancellations
* damaged goods tracking

---

### 7 — Scalability Risks

Identify:

* tables that will grow fastest
* fields that need partitioning later
* queries that will degrade over time

---

### 8 — Future Sales Compatibility

Confirm whether current schema can support:

* sales workflows
* customer billing
* revenue reporting

If not:

Explain required schema changes.

---

### 9 — Audit Capability

Check support for:

* user activity tracking
* inventory history
* financial traceability

---

### 10 — Overall Risk Summary

Provide:

Top 5 risks most likely to cause production failure.

---

# Part 2 — Conversational Query Feature Guidelines

## System Behavior

Users can type natural language queries.

Examples:

* "show me all suppliers"
* "how many shipments are pending"
* "total revenue for January"
* "inventory levels in warehouse Karachi"

System converts:

Natural Language → SQL → Response

Responses may include:

* Tables
* Charts
* Text summaries

This feature requires strong indexing.

Without it, performance will collapse under real data.

---

# Required Indexing Strategy

All foreign keys must be indexed.

Mandatory indexes:

```sql
CREATE INDEX idx_products_supplier
ON products(supplier_id);

CREATE INDEX idx_products_category
ON products(category_id);

CREATE INDEX idx_inventory_product
ON inventory(product_id);

CREATE INDEX idx_inventory_warehouse
ON inventory(warehouse_id);

CREATE INDEX idx_po_supplier
ON purchase_orders(supplier_id);

CREATE INDEX idx_po_warehouse
ON purchase_orders(warehouse_id);

CREATE INDEX idx_invoice_supplier
ON invoices(supplier_id);

CREATE INDEX idx_shipment_po
ON shipments(po_id);
```

---

# Search Optimization Rules

Natural language queries often filter by:

* name
* status
* dates

These fields should be indexed.

Examples:

```sql
CREATE INDEX idx_supplier_name
ON suppliers(supplier_name);

CREATE INDEX idx_product_name
ON products(product_name);

CREATE INDEX idx_po_date
ON purchase_orders(order_date);

CREATE INDEX idx_invoice_date
ON invoices(invoice_date);
```

---

# Aggregation Optimization

Analytics queries often use:

* SUM
* COUNT
* GROUP BY

Indexes must support:

* date ranges
* grouping keys

Recommended:

```sql
CREATE INDEX idx_invoice_date_status
ON invoices(invoice_date, status);

CREATE INDEX idx_shipment_status
ON shipments(status);
```

---

# Future Hashing Strategy

For large datasets:

Use hashing indexes for:

* tracking_number
* sku
* order_number

Example:

```sql
CREATE INDEX idx_product_sku_hash
ON products USING HASH (sku);
```

Use only when:

* equality search required
* not range queries

---

# Part 3 — Development Rules

All new tables must include:

```sql
created_at TIMESTAMP
updated_at TIMESTAMP
deleted BOOLEAN DEFAULT FALSE
```

All foreign keys must:

* be explicitly declared
* be indexed

No exceptions.

---

# Part 4 — Before Schema Changes

Before modifying schema:

1 — Run schema review agent
2 — Generate audit report
3 — Fix critical issues
4 — Apply migration
5 — Run test dataset

Never change schema directly in production.

---

# Part 5 — Recommended Future Improvements

These should be implemented later:

* inventory_transactions table
* stock adjustment logs
* sales module support
* audit logging
* table partitioning for large datasets

---

# Final Rule

Schema quality determines system speed.

Bad schema design cannot be fixed by better hardware.

Fix structure early.
