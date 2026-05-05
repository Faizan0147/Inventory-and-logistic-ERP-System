-- Migration: Replace plain UNIQUE constraints with partial unique indexes
-- Purpose:   Allow re-creation of records with the same unique value after soft-delete
-- Run this ONCE against your existing database.

BEGIN;

-- 1. users.email
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_email_key;
CREATE UNIQUE INDEX IF NOT EXISTS uq_users_email_active
    ON users(email) WHERE deleted = FALSE;

-- 2. products.sku
ALTER TABLE products DROP CONSTRAINT IF EXISTS products_sku_key;
CREATE UNIQUE INDEX IF NOT EXISTS uq_products_sku_active
    ON products(sku) WHERE deleted = FALSE;

-- 3. inventory(product_id, warehouse_id)
ALTER TABLE inventory DROP CONSTRAINT IF EXISTS inventory_product_id_warehouse_id_key;
CREATE UNIQUE INDEX IF NOT EXISTS uq_inventory_product_warehouse_active
    ON inventory(product_id, warehouse_id) WHERE deleted = FALSE;

-- 4. purchase_orders.order_number
ALTER TABLE purchase_orders DROP CONSTRAINT IF EXISTS purchase_orders_order_number_key;
CREATE UNIQUE INDEX IF NOT EXISTS uq_po_order_number_active
    ON purchase_orders(user_id, order_number) WHERE deleted = FALSE;

-- 5. invoices.invoice_number
ALTER TABLE invoices DROP CONSTRAINT IF EXISTS invoices_invoice_number_key;
CREATE UNIQUE INDEX IF NOT EXISTS uq_invoices_invoice_number_active
    ON invoices(invoice_number) WHERE deleted = FALSE;

-- 6. customers.email
ALTER TABLE customers DROP CONSTRAINT IF EXISTS customers_email_key;
CREATE UNIQUE INDEX IF NOT EXISTS uq_customers_email_active
    ON customers(email) WHERE deleted = FALSE;

-- 7. shipments.tracking_number
ALTER TABLE shipments DROP CONSTRAINT IF EXISTS shipments_tracking_number_key;
CREATE UNIQUE INDEX IF NOT EXISTS uq_shipments_tracking_number_active
    ON shipments(tracking_number) WHERE deleted = FALSE;

COMMIT;
