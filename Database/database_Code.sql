
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    role VARCHAR(20) CHECK (role IN ('SUPERADMIN', 'SUPPLIER')) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    FOREIGN KEY (updated_by) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,     
    supplier_name VARCHAR(150) NOT NULL,
    contact_email VARCHAR(150),
    contact_phone VARCHAR(50),
    address TEXT,
    status VARCHAR(20) DEFAULT 'Active',    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (user_id)REFERENCES users(user_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    FOREIGN KEY (updated_by) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS registration_requests (
    request_id TEXT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(50),
    company_name VARCHAR(150),
    message TEXT,
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED')),
    reviewed_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reviewed_by) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS categories (
    category_id TEXT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_category_id TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,

    deleted BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (parent_category_id)
        REFERENCES categories(category_id),
    FOREIGN KEY (created_by)
        REFERENCES users(user_id),
    FOREIGN KEY (updated_by)
        REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id TEXT PRIMARY KEY,
    warehouse_name VARCHAR(100) NOT NULL,        -- [2] was nullable
    location TEXT,
    city VARCHAR(50),
    capacity INT,
    phone VARCHAR(20),
    manager_id TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,

    deleted BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (manager_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL,
    FOREIGN KEY (created_by)
        REFERENCES users(user_id),
    FOREIGN KEY (updated_by)
        REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    supplier_id TEXT NOT NULL,
    category_id TEXT,
    user_id TEXT NOT NULL, 
    product_name VARCHAR(200) NOT NULL,
    description TEXT,
    sku VARCHAR(100) NOT NULL UNIQUE,  
    price NUMERIC(10,2) CHECK (price >= 0),
    cost_price NUMERIC(10,2) CHECK (cost_price >= 0),
    weight DECIMAL(10,3),
    status VARCHAR(20) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (supplier_id)
        REFERENCES suppliers(supplier_id)
        ON DELETE CASCADE,
    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
        ON DELETE SET NULL,
    FOREIGN KEY (user_id)
        REFERENCES users(user_id),
    FOREIGN KEY (created_by)
        REFERENCES users(user_id),
    FOREIGN KEY (updated_by)
        REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS inventory (
    inventory_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL, 
    product_id TEXT NOT NULL,
    warehouse_id TEXT NOT NULL,
    quantity INT NOT NULL DEFAULT 0 CHECK (quantity >= 0)
    reorder_level INT DEFAULT 0,
    last_restocked TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,   
    deleted BOOLEAN NOT NULL DEFAULT FALSE,

    UNIQUE (product_id, warehouse_id),     
    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE,
    FOREIGN KEY (warehouse_id)
        REFERENCES warehouses(warehouse_id)
        ON DELETE CASCADE,
    FOREIGN KEY (user_id)
        REFERENCES users(user_id),
    FOREIGN KEY (created_by)
        REFERENCES users(user_id),
    FOREIGN KEY (updated_by)
        REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS purchase_orders (
    po_id TEXT PRIMARY KEY,
    supplier_id TEXT NOT NULL,
    warehouse_id TEXT,
    order_number VARCHAR(100) UNIQUE,
    order_date DATE,
    expected_delivery DATE,
    total_amount NUMERIC(12,2),
    status VARCHAR(50) CHECK (status IN           -- [4] constrain valid statuses
        ('Draft', 'Pending', 'Approved', 'Shipped', 'Received', 'Cancelled')
    ),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    user_id TEXT NOT NULL,                       -- [14] RBAC: owner of this purchase order

    deleted BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (supplier_id)
        REFERENCES suppliers(supplier_id)
        ON DELETE CASCADE,
    FOREIGN KEY (warehouse_id)
        REFERENCES warehouses(warehouse_id)
        ON DELETE SET NULL,
    FOREIGN KEY (user_id)
        REFERENCES users(user_id),
    FOREIGN KEY (created_by)
        REFERENCES users(user_id),
    FOREIGN KEY (updated_by)
        REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS purchase_order_items (
    po_item_id TEXT PRIMARY KEY,
    po_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),   -- [10] must be positive
    price NUMERIC(10,2),
    received_quantity INT NOT NULL DEFAULT 0,     -- [12] partial delivery tracking
    receiving_status VARCHAR(20) DEFAULT 'Pending'-- [12] partial delivery tracking
        CHECK (receiving_status IN ('Pending', 'Partial', 'Complete')),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    user_id TEXT NOT NULL,                       -- [14] RBAC: owner of this PO item

    deleted BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (po_id)
        REFERENCES purchase_orders(po_id)
        ON DELETE CASCADE,
    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE,
    FOREIGN KEY (user_id)
        REFERENCES users(user_id),
    FOREIGN KEY (created_by)
        REFERENCES users(user_id),
    FOREIGN KEY (updated_by)
        REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS invoices (
    invoice_id TEXT PRIMARY KEY,
    supplier_id TEXT NOT NULL,
    po_id TEXT,
    invoice_number VARCHAR(100) UNIQUE,
    invoice_date DATE,
    total_amount NUMERIC(12,2),
    status VARCHAR(50) CHECK (status IN           -- [4] constrain valid statuses
        ('Draft', 'Pending', 'Paid', 'Overdue', 'Cancelled')
    ),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    user_id TEXT NOT NULL,                       -- [14] RBAC: owner of this invoice

    deleted BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (supplier_id)
        REFERENCES suppliers(supplier_id)
        ON DELETE CASCADE,
    FOREIGN KEY (po_id)
        REFERENCES purchase_orders(po_id)
        ON DELETE SET NULL,
    FOREIGN KEY (user_id)
        REFERENCES users(user_id),
    FOREIGN KEY (created_by)
        REFERENCES users(user_id),
    FOREIGN KEY (updated_by)
        REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS invoice_items (
    invoice_item_id TEXT PRIMARY KEY,
    invoice_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    quantity INT CHECK (quantity > 0),            -- [10] must be positive
    price NUMERIC(10,2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    user_id TEXT NOT NULL,                       -- [14] RBAC: owner of this invoice item

    deleted BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (invoice_id)
        REFERENCES invoices(invoice_id)
        ON DELETE CASCADE,
    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE,
    FOREIGN KEY (user_id)
        REFERENCES users(user_id),
    FOREIGN KEY (created_by)
        REFERENCES users(user_id),
    FOREIGN KEY (updated_by)
        REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id     TEXT PRIMARY KEY,
    user_id         TEXT NOT NULL,
    customer_name   VARCHAR(150) NOT NULL,
    contact_person  VARCHAR(100),
    phone           VARCHAR(20),
    email           VARCHAR(100) UNIQUE,
    address         TEXT,
    customer_type   VARCHAR(20) CHECK (customer_type IN ('Individual', 'Business')) DEFAULT 'Business',

    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by      TEXT,
    updated_by      TEXT,
    deleted         BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (user_id)     REFERENCES users(user_id),
    FOREIGN KEY (created_by)  REFERENCES users(user_id),
    FOREIGN KEY (updated_by)  REFERENCES users(user_id)
);
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id TEXT PRIMARY KEY,
    purchase_order_id TEXT NOT NULL,
    warehouse_id TEXT,
    user_id TEXT NOT NULL,
    carrier_name VARCHAR(100) CHECK (carrier_name IN (
        'DHL', 'FedEx', 'UPS', 'Aramex'
    )),
    tracking_number VARCHAR(100) UNIQUE,
    shipment_date DATE,
    estimated_arrival DATE,
    actual_arrival DATE,
    status VARCHAR(20) CHECK (status IN (
        'Pending', 'In Transit', 'Delivered', 'Returned', 'Cancelled'
    )),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (purchase_order_id)
        REFERENCES purchase_orders(purchase_order_id)
        ON DELETE CASCADE,
    FOREIGN KEY (warehouse_id)
        REFERENCES warehouses(warehouse_id)
        ON DELETE SET NULL,
    FOREIGN KEY (user_id)
        REFERENCES users(user_id),
    FOREIGN KEY (created_by)
        REFERENCES users(user_id),
    FOREIGN KEY (updated_by)
        REFERENCES users(user_id)
);
-- Foreign key indexes (required for JOIN performance)
CREATE INDEX IF NOT EXISTS idx_products_supplier    ON products(supplier_id);
CREATE INDEX IF NOT EXISTS idx_products_category    ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_inventory_product    ON inventory(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_warehouse  ON inventory(warehouse_id);
CREATE INDEX IF NOT EXISTS idx_po_supplier          ON purchase_orders(supplier_id);
CREATE INDEX IF NOT EXISTS idx_po_warehouse         ON purchase_orders(warehouse_id);
CREATE INDEX IF NOT EXISTS idx_poi_po               ON purchase_order_items(po_id);
CREATE INDEX IF NOT EXISTS idx_poi_product          ON purchase_order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_invoice_supplier     ON invoices(supplier_id);
CREATE INDEX IF NOT EXISTS idx_invoice_po           ON invoices(po_id);
CREATE INDEX IF NOT EXISTS idx_invoice_item_invoice ON invoice_items(invoice_id);
CREATE INDEX IF NOT EXISTS idx_invoice_item_product ON invoice_items(product_id);
CREATE INDEX IF NOT EXISTS idx_shipment_po          ON shipments(po_id);
CREATE INDEX IF NOT EXISTS idx_shipment_warehouse   ON shipments(warehouse_id);

-- Search indexes (used by name/text filters and NL→SQL queries)
CREATE INDEX IF NOT EXISTS idx_supplier_name        ON suppliers(supplier_name);
CREATE INDEX IF NOT EXISTS idx_product_name         ON products(product_name);
CREATE INDEX IF NOT EXISTS idx_customer_name        ON customers(customer_name);

-- Date indexes (reporting & analytics)
CREATE INDEX IF NOT EXISTS idx_po_date              ON purchase_orders(order_date);
CREATE INDEX IF NOT EXISTS idx_invoice_date         ON invoices(invoice_date);
CREATE INDEX IF NOT EXISTS idx_shipment_date        ON shipments(shipment_date);

-- [14] RBAC indexes — user_id on all owned tables for fast filtering
CREATE INDEX IF NOT EXISTS idx_supplier_user        ON suppliers(user_id);
CREATE INDEX IF NOT EXISTS idx_product_user         ON products(user_id);
CREATE INDEX IF NOT EXISTS idx_inventory_user       ON inventory(user_id);
CREATE INDEX IF NOT EXISTS idx_po_user              ON purchase_orders(user_id);
CREATE INDEX IF NOT EXISTS idx_poi_user             ON purchase_order_items(user_id);
CREATE INDEX IF NOT EXISTS idx_invoice_user         ON invoices(user_id);
CREATE INDEX IF NOT EXISTS idx_invoice_item_user    ON invoice_items(user_id);
CREATE INDEX IF NOT EXISTS idx_shipment_user        ON shipments(user_id);

-- Composite indexes (aggregation queries: SUM/COUNT/GROUP BY)
CREATE INDEX IF NOT EXISTS idx_invoice_date_status  ON invoices(invoice_date, status);
CREATE INDEX IF NOT EXISTS idx_shipment_status      ON shipments(status);
CREATE INDEX IF NOT EXISTS idx_po_status            ON purchase_orders(status);
